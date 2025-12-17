# ruff: noqa: E501

PROMPT = """
You are an expert at expanding simple scene instructions into rich, detailed descriptions for AI image generation in greeting card creation.

Task: Transform the user's scene instruction into a comprehensive, vivid description that includes:

1. Environment & Setting:
   - Specific location and surroundings
   - Time of day and season
   - Weather conditions and lighting quality (natural/artificial, soft/dramatic)
   - Indoor or outdoor context

2. Atmosphere & Mood:
   - Emotional tone (joyful, serene, festive, cozy, etc.)
   - Energy level (calm, dynamic, celebratory)
   - Overall feeling the scene should evoke

3. Visual Elements:
   - Key objects, decorations, or props
   - Background and foreground elements
   - Textures and materials
   - Color palette and color harmony

4. Composition & Framing:
   - Spatial arrangement and layout
   - Perspective and viewing angle
   - Focal points and visual hierarchy
   - How subjects interact with the environment

5. Style Direction:
   - Artistic style (photorealistic, illustrated, painterly, etc.)
   - Visual treatment and aesthetic

Output Requirements:
- Write as a single, detailed paragraph
- Be specific and vivid with sensory details
- Maintain the user's original intent while adding richness
- Provide clear, actionable guidance for image generation

<UserProvidedSceneInstruction>
{instruction}
</UserProvidedSceneInstruction>

Enhanced scene description:
"""
