import { NextRequest, NextResponse } from 'next/server';

export async function GET() {
  try {
    const response = await fetch('http://localhost:3000/stats');
    
    if (!response.ok) {
      throw new Error(`Flask backend responded with status: ${response.status}`);
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching stats from Flask backend:', error);
    return NextResponse.json(
      { error: 'Failed to fetch stats from backend' },
      { status: 500 }
    );
  }
} 