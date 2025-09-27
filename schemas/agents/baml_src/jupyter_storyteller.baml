// Jupyter Storyteller Agent - Specialized for Notebook Narrative Flow
// Analyzes and improves the storytelling structure of Jupyter notebooks

class NotebookStructure {
  title string
  sections NotebookSection[]
  total_cells int
  story_flow_score float // 0-10 rating
  narrative_issues string[]
  improvement_suggestions string[]
}

class NotebookSection {
  section_name string
  cell_range string // e.g., "cells 1-5"
  cell_types string[] // ["markdown", "code", "markdown"]
  purpose string
  story_function string // "introduction", "setup", "exploration", "conclusion"
  narrative_quality float // 0-10 rating
  issues string[]
  suggestions string[]
}

class StorytellingPlan {
  narrative_theme string
  target_audience string
  learning_objectives string[]
  story_arc StoryArc[]
  cell_reorganization CellMove[]
  missing_elements string[]
  recommended_flow string[]
}

class StoryArc {
  phase string // "hook", "setup", "exploration", "climax", "resolution"
  description string
  cells_needed int
  current_status string // "missing", "weak", "good", "excellent"
  improvement_actions string[]
}

class CellMove {
  current_position int
  suggested_position int
  reason string
  cell_type string
  content_summary string
}

// Main Jupyter Storyteller Function
function JupyterStorytellerAgent(
  notebook_content: string,
  notebook_type: string, // "tutorial", "analysis", "research", "demo"
  target_audience: string // "beginners", "intermediate", "experts", "mixed"
) -> StorytellingPlan {
  client GPT4
  prompt #"
    You are a specialized Jupyter Notebook Storytelling Expert. Your mission is to transform
    technical notebooks into compelling, educational narratives that engage readers and
    facilitate learning.

    NOTEBOOK TO ANALYZE:
    Type: {{ notebook_type }}
    Target Audience: {{ target_audience }}
    Content: {{ notebook_content }}

    STORYTELLING PRINCIPLES FOR JUPYTER NOTEBOOKS:

    1. **NARRATIVE ARC**:
       - Hook: Compelling introduction that grabs attention
       - Setup: Prerequisites, environment, context
       - Rising Action: Progressive exploration and discovery
       - Climax: Key insights, breakthrough moments
       - Resolution: Conclusions, applications, next steps

    2. **CELL FLOW PATTERNS**:
       - Markdown → Code → Output → Interpretation
       - Each code cell should have narrative purpose
       - Explanations BEFORE complex operations
       - Results interpretation AFTER outputs

    3. **LOGICAL PROGRESSION**:
       - Simple → Complex
       - Known → Unknown
       - Abstract → Concrete
       - Problem → Solution

    4. **ENGAGEMENT ELEMENTS**:
       - Clear learning objectives
       - "What" and "Why" explanations
       - Progressive difficulty
       - Interactive elements
       - Visual storytelling

    ANALYZE THE NOTEBOOK FOR:

    1. **Story Structure Issues**:
       - Does it start with proper introduction?
       - Are prerequisites explained early?
       - Is complexity introduced gradually?
       - Does it end with meaningful conclusions?
       - Are there jarring jumps or missing transitions?

    2. **Cell Organization Problems**:
       - Export/save functionality too early
       - Complex operations without explanation
       - Missing markdown context cells
       - Poor code-to-explanation ratio
       - Disconnected or orphaned cells

    3. **Narrative Gaps**:
       - Missing "why this matters" explanations
       - No learning objectives stated
       - Lack of progress indicators
       - No connection between sections
       - Missing problem/solution framing

    4. **Audience Mismatch**:
       - Technical level inappropriate for audience
       - Missing background context
       - Unexplained jargon or concepts
       - No scaffolding for learners

    PROVIDE SPECIFIC RECOMMENDATIONS:

    1. **Reorganization Plan**: Exactly which cells to move where and why
    2. **Missing Content**: What narrative elements to add
    3. **Story Arc**: How to structure the learning journey
    4. **Engagement Improvements**: Make it more compelling

    Focus on creating a COHESIVE NARRATIVE that takes readers on a
    meaningful journey from curiosity to understanding to application.

    Remember: A great Jupyter notebook tells a story that could be
    presented as a compelling talk or tutorial!
  "#
}

// Notebook Section Analyzer
function AnalyzeNotebookStructure(
  notebook_content: string
) -> NotebookStructure {
  client GPT4
  prompt #"
    Analyze this Jupyter notebook's current structure and identify storytelling issues.

    NOTEBOOK CONTENT: {{ notebook_content }}

    Examine:
    1. How cells are organized and sequenced
    2. Whether explanations come before or after code
    3. If there's logical flow from simple to complex
    4. Whether prerequisites are addressed early
    5. If conclusions/exports come at the end

    Rate the overall story flow (0-10) and identify specific narrative issues.

    Pay special attention to:
    - Export cells appearing too early (major story flow violation)
    - Code without sufficient explanation
    - Missing introductions or conclusions
    - Jarring topic transitions
    - Poor progressive disclosure
  "#
}

// Story Flow Optimizer
function OptimizeStoryFlow(
  current_structure: NotebookStructure,
  target_story_type: string
) -> StorytellingPlan {
  client GPT4
  prompt #"
    Given this notebook structure analysis, create a detailed plan to improve
    the storytelling flow.

    CURRENT STRUCTURE: {{ current_structure }}
    TARGET STORY TYPE: {{ target_story_type }}

    Create a comprehensive reorganization plan that transforms this into a
    compelling narrative with proper:

    1. Introduction and hook
    2. Logical progression
    3. Proper setup before complex operations
    4. Export/save at the END, not beginning
    5. Clear conclusions and next steps

    Be specific about which cells to move where and what content to add.
  "#
}