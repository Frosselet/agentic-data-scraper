import { NextRequest, NextResponse } from 'next/server'
import { spawn } from 'child_process'
import path from 'path'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const {
      question,
      successCriteria,
      timeline,
      budget,
      riskTolerance,
      personaId
    } = body

    // Validate required fields
    if (!question || !successCriteria || !timeline || !budget || !riskTolerance || !personaId) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      )
    }

    // Call BAML BusinessContextAgent via Python
    const result = await callBAMLAgent('BusinessContextAgent', {
      business_question: question,
      success_criteria: successCriteria,
      timeline: timeline,
      budget: budget,
      risk_tolerance: riskTolerance,
      persona_id: personaId
    })

    return NextResponse.json({
      success: true,
      data: result
    })

  } catch (error) {
    console.error('Business context API error:', error)
    return NextResponse.json(
      { error: 'Failed to process business context' },
      { status: 500 }
    )
  }
}

async function callBAMLAgent(agentName: string, params: Record<string, any>): Promise<any> {
  return new Promise((resolve, reject) => {
    const pythonScript = `
import asyncio
import json
import sys
import os

# Add the parent directory to Python path to import baml_client
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../..'))

from baml_client import b

async def main():
    try:
        # Parse parameters from command line
        params = json.loads(sys.argv[1])
        
        # Call the appropriate BAML agent
        if sys.argv[2] == 'BusinessContextAgent':
            result = await b.BusinessContextAgent(
                business_question=params['business_question'],
                success_criteria=params['success_criteria'],
                timeline=params['timeline'],
                budget=params['budget'],
                risk_tolerance=params['risk_tolerance'],
                persona_id=params['persona_id']
            )
        else:
            raise ValueError(f"Unknown agent: {sys.argv[2]}")
        
        # Convert result to dict if it's a Pydantic model
        if hasattr(result, 'model_dump'):
            result_dict = result.model_dump()
        else:
            result_dict = result
            
        print(json.dumps(result_dict))
        
    except Exception as e:
        error_result = {
            "error": str(e),
            "type": type(e).__name__
        }
        print(json.dumps(error_result))
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
`

    // Get the path to the Python project
    const projectRoot = path.resolve(process.cwd(), '../..')
    
    // Spawn Python process with UV
    const python = spawn('uv', ['run', 'python', '-c', pythonScript, JSON.stringify(params), agentName], {
      cwd: projectRoot,
      stdio: ['pipe', 'pipe', 'pipe']
    })

    let stdout = ''
    let stderr = ''

    python.stdout.on('data', (data) => {
      stdout += data.toString()
    })

    python.stderr.on('data', (data) => {
      stderr += data.toString()
    })

    python.on('close', (code) => {
      if (code === 0) {
        try {
          const result = JSON.parse(stdout.trim())
          if (result.error) {
            reject(new Error(result.error))
          } else {
            resolve(result)
          }
        } catch (parseError) {
          reject(new Error(`Failed to parse Python output: ${stdout}`))
        }
      } else {
        reject(new Error(`Python process failed with code ${code}: ${stderr}`))
      }
    })

    python.on('error', (error) => {
      reject(new Error(`Failed to start Python process: ${error.message}`))
    })
  })
}