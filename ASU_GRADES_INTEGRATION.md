# ASU Grades Data Integration

This document describes the integration of ASU grades data into the PagerLifeLLM RAG (Retrieval-Augmented Generation) system.

## Overview

The ASU grades data integration adds comprehensive course grade information and professor ratings to the RAG system, enabling users to query about:

- Course grade distributions and statistics
- Professor ratings and reviews
- Course difficulty and pass rates
- Historical grade trends across semesters

## Data Sources

### 1. Course Grade Data (CSV Files)
- **Location**: `data/raw/raw_asu_grades/`
- **Format**: Semester-by-semester CSV files (e.g., "Fall 2024.csv")
- **Content**: Grade distributions for each course section including:
  - Subject and catalog number
  - Section information
  - Grade counts (A+, A, A-, B+, B, B-, C+, C, C-, D+, D, D-, F)
  - Instructor names
  - Total enrollment

### 2. Professor Data (JSON File)
- **Location**: `data/raw/raw_asu_grades/matched_professor_data.json`
- **Content**: RateMyProfessors data matched to ASU instructors including:
  - Quality and difficulty ratings
  - Student tags and reviews
  - Course-specific ratings
  - Department information

## Data Processing

### ASUGradesProcessor Class

The `src/utils/asu_grades_processor.py` file contains the main processing logic:

#### Key Features:
- **Course Document Generation**: Creates structured documents for each course section
- **Professor Document Generation**: Creates documents for professor information
- **Grade Statistics Calculation**: Computes average grades, pass rates, and distributions
- **Data Integration**: Links course data with professor ratings

#### Document Structure:

**Course Documents:**
```python
{
    'id': 'ACCT_2301_001_Fall_2024',
    'content': 'Course: ACCT 2301 Section 001\nSemester: Fall 2024\n...',
    'metadata': {
        'course_code': 'ACCT 2301',
        'subject': 'ACCT',
        'catalog_nbr': '2301',
        'section': '001',
        'semester': 'Fall',
        'year': '2024',
        'instructors': ['Huang, Ying'],
        'total_students': 45,
        'average_grade': 3.2,
        'pass_rate': 95.6,
        'grade_distribution': {...},
        'professor_info': {...}
    },
    'source': 'asu_grades'
}
```

**Professor Documents:**
```python
{
    'id': 'professor_12345',
    'content': 'Professor: John Smith\nDepartment: Computer Science\n...',
    'metadata': {
        'professor_name': 'John Smith',
        'department': 'Computer Science',
        'quality_rating': 4.2,
        'difficulty_rating': 3.1,
        'would_take_again': 85,
        'tags': ['Great lectures', 'Fair grader'],
        'course_ratings': {...}
    },
    'source': 'asu_grades_professors'
}
```

## Integration with RAG System

### Updated Components:

1. **RAG System** (`src/rag/rag_system.py`):
   - Added `ASUGradesProcessor` initialization
   - Added "asu_grades" data source handling

2. **Build Scripts**:
   - `scripts/build_rag.py`: Now includes "asu_grades" by default
   - `scripts/build_grades_rag.py`: Builds RAG with grades data only

### Data Flow:

1. **Ingestion**: CSV files and professor JSON are processed
2. **Document Creation**: Structured documents are generated
3. **Embedding**: Text content is converted to vector embeddings
4. **Storage**: Documents and embeddings are stored in vector database
5. **Retrieval**: Queries can retrieve relevant grade/professor information

## Usage

### Processing Grades Data

```bash
# Process and embed grades data only
python scripts/process_asu_grades.py

# Build RAG system with all data sources including grades
python scripts/build_rag.py

# Build RAG system with grades data only
python scripts/build_grades_rag.py
```

### Testing

```bash
# Test data processing without embeddings
python scripts/test_grades_processing.py

# Test full RAG system with grades data
python scripts/test_grades_rag.py
```

### Query Examples

Once integrated, the RAG system can answer queries like:

- "What is the average grade for MAT 210?"
- "Who teaches ACCT 2301 and what are their ratings?"
- "Which courses have the highest pass rates?"
- "What is the grade distribution for CS 110?"
- "Which professors have the best ratings in Computer Science?"
- "How do grades compare between Fall 2023 and Fall 2024?"

## Data Statistics

Based on the current dataset:

- **Course Documents**: ~25,559 (across all semesters)
- **Professor Documents**: ~2,581
- **Time Range**: 2017-2024
- **Subjects**: 130 unique subjects
- **Departments**: 68 departments with professor data
- **Semesters**: Fall, Spring, Summer

## File Structure

```
src/utils/
├── asu_grades_processor.py    # Main processing logic
└── data_processor.py          # Original processor (unchanged)

scripts/
├── process_asu_grades.py      # Process and embed grades data
├── test_grades_processing.py  # Test data processing
├── test_grades_rag.py         # Test RAG queries
├── build_grades_rag.py        # Build RAG with grades only
└── build_rag.py               # Build RAG with all sources

data/raw/raw_asu_grades/
├── Fall 2017.csv              # Semester grade files
├── Spring 2018.csv
├── ...
├── Summer 2024.csv
└── matched_professor_data.json # Professor ratings data
```

## Configuration

The integration uses the existing configuration in `config/settings.py`:

- `CHUNK_SIZE`: Text chunking for embeddings
- `CHUNK_OVERLAP`: Overlap between chunks
- `EMBEDDING_MODEL`: Model for generating embeddings
- `VECTOR_DB_DIR`: Directory for vector database storage

## Error Handling

The processor includes robust error handling for:

- Missing or corrupted CSV files
- Invalid grade values (decimal strings, etc.)
- Missing professor data
- Malformed JSON data

## Future Enhancements

Potential improvements:

1. **Grade Trend Analysis**: Track grade changes over time
2. **Course Difficulty Scoring**: Algorithmic difficulty assessment
3. **Professor Performance Metrics**: Grade-based professor evaluation
4. **Course Recommendations**: Suggest courses based on grades and ratings
5. **Department Comparisons**: Compare performance across departments

## Troubleshooting

### Common Issues:

1. **Missing API Key**: Set `OPENAI_API_KEY` environment variable
2. **File Not Found**: Ensure CSV files are in `data/raw/raw_asu_grades/`
3. **Memory Issues**: Process data in smaller batches for large datasets
4. **Embedding Failures**: Check API quota and network connectivity

### Logs:

- Processing logs: `asu_grades_processing.log`
- General logs: `asu_rag.log`

## Contributing

When adding new data sources or modifying the processor:

1. Follow the existing document structure
2. Add appropriate error handling
3. Update this documentation
4. Test with sample data
5. Update build scripts if needed 