import os
import json
import csv
import pandas as pd
from typing import List, Dict, Any, Generator
from dataclasses import dataclass
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class Document:
    """Represents a processed document for RAG"""
    id: str
    content: str
    metadata: Dict[str, Any]
    source: str

class ASUGradesProcessor:
    """Processes ASU grades data into RAG-ready format"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.professor_data = {}
        self._load_professor_data()
    
    def _load_professor_data(self):
        """Load professor data from JSON file"""
        professor_file = "data/raw/raw_asu_grades/matched_professor_data.json"
        if os.path.exists(professor_file):
            try:
                with open(professor_file, 'r', encoding='utf-8') as f:
                    self.professor_data = json.load(f)
                logger.info(f"Loaded professor data for {len(self.professor_data)} professors")
            except Exception as e:
                logger.error(f"Error loading professor data: {e}")
    
    def _get_professor_info(self, instructor_name: str) -> Dict[str, Any]:
        """Get professor information from the matched data"""
        if not instructor_name or not self.professor_data:
            return {}
        
        # Normalize instructor name for lookup
        normalized_name = instructor_name.lower().strip()
        
        # Try exact match first
        if normalized_name in self.professor_data:
            return self.professor_data[normalized_name][0] if self.professor_data[normalized_name] else {}
        
        # Try partial matches
        for prof_name, prof_data in self.professor_data.items():
            if prof_name in normalized_name or normalized_name in prof_name:
                return prof_data[0] if prof_data else {}
        
        return {}
    
    def _calculate_grade_stats(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate grade statistics from a row"""
        grade_columns = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F']
        
        total_students = 0
        grade_counts = {}
        
        for grade in grade_columns:
            try:
                count = int(float(row.get(grade, 0) or 0))
                grade_counts[grade] = count
                total_students += count
            except (ValueError, TypeError):
                # Handle cases where the value might be a decimal string or invalid
                count = 0
                grade_counts[grade] = count
        
        if total_students == 0:
            return {
                'total_students': 0,
                'average_grade': 'N/A',
                'pass_rate': 0,
                'grade_distribution': grade_counts
            }
        
        # Calculate pass rate (A+ through D-)
        passing_grades = sum(grade_counts[grade] for grade in grade_counts.keys())
        pass_rate = (passing_grades / total_students) * 100 if total_students > 0 else 0
        
        # Calculate average grade (simplified)
        grade_points = {
            'A+': 4.33, 'A': 4.0, 'A-': 3.67,
            'B+': 3.33, 'B': 3.0, 'B-': 2.67,
            'C+': 2.33, 'C': 2.0, 'C-': 1.67,
            'D+': 1.33, 'D': 1.0, 'D-': 0.67,
            'F': 0.0
        }
        
        total_points = sum(grade_counts[grade] * grade_points[grade] for grade in grade_counts.keys())
        average_grade = total_points / total_students if total_students > 0 else 0
        
        return {
            'total_students': total_students,
            'average_grade': round(average_grade, 2),
            'pass_rate': round(pass_rate, 1),
            'grade_distribution': grade_counts
        }
    
    def _create_course_document(self, row: Dict[str, Any], semester: str, year: str) -> Document:
        """Create a document for a single course section"""
        subject = row.get('Subject', '')
        catalog_nbr = row.get('Catalog Nbr', '')
        section = row.get('Section', '')
        course_code = f"{subject} {catalog_nbr}"
        
        # Get instructor information
        instructors = []
        for i in range(1, 7):  # Instructor 1-6
            instructor = row.get(f'Instructor {i}', '').strip()
            if instructor:
                instructors.append(instructor)
        
        # Calculate grade statistics
        stats = self._calculate_grade_stats(row)
        
        # Get professor info for first instructor
        professor_info = {}
        if instructors:
            professor_info = self._get_professor_info(instructors[0])
        
        # Create content
        content_parts = [
            f"Course: {course_code} Section {section}",
            f"Semester: {semester} {year}",
            f"Total Students: {stats['total_students']}",
            f"Average Grade: {stats['average_grade']}",
            f"Pass Rate: {stats['pass_rate']}%"
        ]
        
        if instructors:
            content_parts.append(f"Instructors: {', '.join(instructors)}")
            
            if professor_info:
                content_parts.extend([
                    f"Professor Rating: {professor_info.get('quality_rating', 'N/A')}/5.0",
                    f"Difficulty Rating: {professor_info.get('difficulty_rating', 'N/A')}/5.0",
                    f"Would Take Again: {professor_info.get('would_take_again', 'N/A')}%"
                ])
                
                if professor_info.get('tags'):
                    content_parts.append(f"Tags: {', '.join(professor_info['tags'])}")
        
        # Add grade distribution
        grade_dist = stats['grade_distribution']
        grade_summary = []
        for grade, count in grade_dist.items():
            if count > 0:
                percentage = (count / stats['total_students']) * 100
                grade_summary.append(f"{grade}: {count} students ({percentage:.1f}%)")
        
        if grade_summary:
            content_parts.append(f"Grade Distribution: {'; '.join(grade_summary)}")
        
        content = "\n".join(content_parts)
        
        # Create metadata
        metadata = {
            'id': f"{course_code}_{section}_{semester}_{year}",
            'course_code': course_code,
            'subject': subject,
            'catalog_nbr': catalog_nbr,
            'section': section,
            'semester': semester,
            'year': year,
            'instructors': instructors,
            'total_students': stats['total_students'],
            'average_grade': stats['average_grade'],
            'pass_rate': stats['pass_rate'],
            'grade_distribution': stats['grade_distribution'],
            'professor_info': professor_info,
            'source': 'asu_grades',
            'processed_at': datetime.now().isoformat()
        }
        
        return Document(
            id=metadata['id'],
            content=content,
            metadata=metadata,
            source='asu_grades'
        )
    
    def _create_professor_document(self, professor_name: str, prof_data: Dict[str, Any]) -> Document:
        """Create a document for professor information"""
        content_parts = [
            f"Professor: {prof_data.get('original_rmp_format', professor_name)}",
            f"Department: {prof_data.get('department', 'N/A')}",
            f"Quality Rating: {prof_data.get('quality_rating', 'N/A')}/5.0",
            f"Difficulty Rating: {prof_data.get('difficulty_rating', 'N/A')}/5.0",
            f"Would Take Again: {prof_data.get('would_take_again', 'N/A')}%",
            f"Number of Ratings: {prof_data.get('ratings_count', 'N/A')}",
            f"Overall Grade Rating: {prof_data.get('overall_grade_rating', 'N/A')}/5.0",
            f"Total Grade Count: {prof_data.get('total_grade_count', 'N/A')}"
        ]
        
        if prof_data.get('tags'):
            content_parts.append(f"Student Tags: {', '.join(prof_data['tags'])}")
        
        if prof_data.get('course_ratings'):
            course_ratings = prof_data['course_ratings']
            ratings_text = [f"{course}: {rating}/5.0" for course, rating in course_ratings.items()]
            content_parts.append(f"Course Ratings: {'; '.join(ratings_text)}")
        
        content = "\n".join(content_parts)
        
        metadata = {
            'id': f"professor_{prof_data.get('rmp_id', professor_name)}",
            'professor_name': prof_data.get('original_rmp_format', professor_name),
            'department': prof_data.get('department'),
            'quality_rating': prof_data.get('quality_rating'),
            'difficulty_rating': prof_data.get('difficulty_rating'),
            'would_take_again': prof_data.get('would_take_again'),
            'ratings_count': prof_data.get('ratings_count'),
            'overall_grade_rating': prof_data.get('overall_grade_rating'),
            'total_grade_count': prof_data.get('total_grade_count'),
            'tags': prof_data.get('tags', []),
            'course_ratings': prof_data.get('course_ratings', {}),
            'rmp_id': prof_data.get('rmp_id'),
            'instructor_id': prof_data.get('instructor_id'),
            'source': 'asu_grades_professors',
            'processed_at': datetime.now().isoformat()
        }
        
        return Document(
            id=metadata['id'],
            content=content,
            metadata=metadata,
            source='asu_grades_professors'
        )
    
    def process_grades_data(self, grades_dir: str = "data/raw/raw_asu_grades") -> Generator[Document, None, None]:
        """Process all grade CSV files"""
        logger.info(f"Processing ASU grades data from {grades_dir}")
        
        if not os.path.exists(grades_dir):
            logger.warning(f"Grades directory not found: {grades_dir}")
            return
        
        # Process CSV files
        csv_files = [f for f in os.listdir(grades_dir) if f.endswith('.csv')]
        
        for csv_file in csv_files:
            file_path = os.path.join(grades_dir, csv_file)
            
            # Extract semester and year from filename
            # Expected format: "Fall 2024.csv" or "Spring 2023.csv"
            filename = csv_file.replace('.csv', '')
            parts = filename.split()
            if len(parts) >= 2:
                semester = parts[0]
                year = parts[1]
            else:
                semester = "Unknown"
                year = "Unknown"
            
            logger.info(f"Processing {csv_file} ({semester} {year})")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row.get('Subject') and row.get('Catalog Nbr'):  # Skip empty rows
                            doc = self._create_course_document(row, semester, year)
                            yield doc
                            
            except Exception as e:
                logger.error(f"Error processing {csv_file}: {e}")
                continue
    
    def process_professor_data(self) -> Generator[Document, None, None]:
        """Process professor data from JSON file"""
        logger.info("Processing professor data")
        
        for professor_name, prof_data_list in self.professor_data.items():
            if prof_data_list:
                prof_data = prof_data_list[0]  # Take first entry
                doc = self._create_professor_document(professor_name, prof_data)
                yield doc
    
    def process_all_grades_data(self) -> Generator[Document, None, None]:
        """Process both grades and professor data"""
        # Process course grades
        yield from self.process_grades_data()
        
        # Process professor information
        yield from self.process_professor_data() 