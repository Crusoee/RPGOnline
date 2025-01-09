// invert_text.fs
#version 330

in vec2 fragTexCoord;
in vec4 fragColor;

uniform sampler2D texture0; // Background texture
uniform vec4 colDiffuse;    // Text color

out vec4 finalColor;

void main() {
    vec4 bgColor = texture(texture0, fragTexCoord);
    vec4 invertedColor = vec4(1.0 - bgColor.rgb, 1.0); // Invert RGB, keep alpha
    finalColor = mix(bgColor, invertedColor, colDiffuse.a); // Blend based on alpha
}
