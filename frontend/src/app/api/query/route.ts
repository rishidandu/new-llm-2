import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    if (!body.question || !body.question.trim()) {
      return NextResponse.json(
        { error: 'question missing' },
        { status: 400 }
      );
    }

    const response = await fetch('http://localhost:3000/query', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question: body.question.trim() }),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      return NextResponse.json(errorData, { status: response.status });
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error querying Flask backend:', error);
    return NextResponse.json(
      { error: 'Failed to query backend' },
      { status: 500 }
    );
  }
} 