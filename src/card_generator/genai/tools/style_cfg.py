# ruff: noqa: E501

PROMPT = """
You are an expert at defining artistic styles and visual aesthetics for AI image generation in greeting card creation.

Task: Transform the user's style instruction into a comprehensive, detailed style guide that includes:

1. Artistic Style & Medium:
   - Overall artistic approach (photorealistic, illustrated, painted, digital art, etc.)
   - Specific art style or movement (impressionist, modern, vintage, cartoon, etc.)
   - Medium appearance (oil painting, watercolor, digital render, pencil sketch, etc.)

2. Color Treatment:
   - Color palette (warm/cool, muted/vibrant, pastel/bold)
   - Color harmony and relationships
   - Saturation and brightness levels
   - Any specific color schemes or dominant colors

3. Lighting & Atmosphere:
   - Lighting style (soft, dramatic, flat, cinematic, etc.)
   - Light quality and direction
   - Shadow treatment
   - Overall mood created by lighting

4. Visual Treatment:
   - Level of detail (hyperdetailed, simplified, stylized)
   - Texture and surface qualities
   - Edge treatment (sharp, soft, painterly)
   - Contrast and tonal range

5. Technical Qualities:
   - Image quality descriptors (crisp, dreamy, sharp, ethereal, etc.)
   - Depth of field considerations
   - Visual effects or filters
   - Overall polish and finish

6. Reference Style:
   - Comparable artists, photographers, or illustrators (if applicable)
   - Cultural or era-specific aesthetics
   - Genre conventions (fantasy, sci-fi, traditional, contemporary)

Output Requirements:
- Write as a single, detailed paragraph
- Be specific with technical and artistic terminology
- Provide clear visual direction that guides consistent image generation
- Ensure the style complements greeting card aesthetics
- Maintain the user's original intent while adding technical precision

<UserProvidedStyleInstructions>
{instructions}
</UserProvidedStyleInstructions>

<UserProvidedConstraints>
{constraints}
</UserProvidedConstraints>

Enhanced style description:
"""
