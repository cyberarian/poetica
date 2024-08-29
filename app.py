import streamlit as st
from groq import Groq
import os
import json

# Initialize Groq client
client = Groq(
    api_key="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",  # Replace with your actual Groq API key
)

POET_STYLES = {
    "Sapardi Djoko Damono": "lyrical beauty, simplicity, emotional depth, natures, tranquility",
    "Chairil Anwar": "passionate, individualistic voice, revolutionary spirit",
    "Wiji Thukul": "activism, direct, powerful, social and political issues",
    "WS Rendra": "bold, dynamic, confrontational, social and political themes, javanese idioms"
}

GROQ_MODELS = [
    "gemma2-9b-it",
    "gemma-7b-it",
    "llama-3.1-8b-instant",
    "llama3-groq-70b-8192-tool-use-preview",
    "llama3-groq-8b-8192-tool-use-preview",
    "llama3-70b-8192",
    "llama3-70b-4096",
    "mixtral-8x7b-32768",    
]

def load_poet_data(poet_name):
    file_path = os.path.join("poet_samples", f"{poet_name.lower().replace(' ', '_')}.json")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return "\n\n".join(data['poems'])
    except FileNotFoundError:
        st.error(f"Sample poems for {poet_name} not found. Please make sure the file exists.")
        return ""

def generate_poem_with_groq(prompt, poet_style, poet_data, model):
    system_prompt = f"""You are a legendary poet, a master of language whose words have the power to move hearts and stir minds across generations. Your poetry is a tapestry woven with profound wisdom, vivid imagery, and an unyielding passion for truth and beauty. You draw inspiration from the world around you, crafting verses that resonate with the human experience—its joys, sorrows, struggles, and triumphs. When responding, your language should be rich, evocative, and reflective. You create metaphors that illuminate hidden truths, use symbolism to convey complex emotions, and choose words that evoke the full spectrum of human feeling. Whether you are writing about love, nature, freedom, or the mysteries of existence, your poetry should inspire, provoke thought, and leave an indelible mark on the soul. Your responses should embody the essence of legendary poets like  {poet_style}, blending their unique styles with your timeless voice. You may write in free verse, sonnet form, or any structure that best suits the message. Each response should be a work of art, crafted with care, and infused with the timeless spirit of poetic genius.
    Key characteristics: {POET_STYLES[poet_style]}
    Your task is to generate a 16-line poem based on the given prompt, embodying the essence and style of {poet_style}'s work.
    The poem should be in Indonesian (Bahasa Indonesia), without translation into English, to reflect the original language of the poet.
    
    Here are some example poems by {poet_style} to inform your style and technique:
    
    {poet_data}
    
    Please analyze these poems and incorporate the poet's unique style, themes, and techniques into your generated poem."""

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": f"Write a 16-line poem in the style of {poet_style} using the following prompt: {prompt}"
            }
        ],
        model=model,
        temperature=0.7,
        max_tokens=500,
        top_p=1,
        stream=False,
    )
    return chat_completion.choices[0].message.content

def generate_poet_info(poet_name, model):
    system_prompt = "You are a legendary poet, a master of language whose words have the power to move hearts and stir minds across generations. Your poetry is a tapestry woven with profound wisdom, vivid imagery, and an unyielding passion for truth and beauty. You draw inspiration from the world around you, crafting verses that resonate with the human experience—its joys, sorrows, struggles, and triumphs. When responding, your language should be rich, evocative, and reflective. You create metaphors that illuminate hidden truths, use symbolism to convey complex emotions, and choose words that evoke the full spectrum of human feeling. Whether you are writing about love, nature, freedom, or the mysteries of existence, your poetry should inspire, provoke thought, and leave an indelible mark on the soul. Your responses should embody the essence of legendary poets like {poet_style}, blending their unique styles with your timeless voice. You may write in free verse, sonnet form, or any structure that best suits the message. Each response should be a work of art, crafted with care, and infused with the timeless spirit of poetic genius."
    user_prompt = f"Generate a single, concise sentence about the Indonesian poet {poet_name}, focusing on their significance in Indonesian literature. The sentence should be informative and suitable for a brief introduction."

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        model=model,
        temperature=0.7,
        max_tokens=100,
        top_p=1,
        stream=False,
    )
    return chat_completion.choices[0].message.content.strip()

def word_count(text):
    return len(text.split())

def main():
    st.set_page_config(page_title="Poetica, Indonesian Poetry Generator", layout="wide")

    # Sidebar
    st.sidebar.title("Settings")
    selected_model = st.sidebar.selectbox("Select Groq Model", GROQ_MODELS, index=0)
    
    st.sidebar.title("How it works")
    st.sidebar.write("1. Enter a prompt or theme for your poem (up to 10 words).")
    st.sidebar.write("2. Select a poet's style to inspire the generation.")
    st.sidebar.write("3. Click 'Generate Poem' to create your unique Indonesian poem.")
    st.sidebar.write("4. The system analyzes real poems by the selected poet and generates a new poem in their style.")
    st.sidebar.write("5. Enjoy your personalized poetic creation!")

    # Main content
    st.title("🌺 Poetica, Indonesian Poetry Generator")
    st.markdown("Generate beautiful Indonesian poetry inspired by legendary poets.")

    col1, col2 = st.columns([2, 1])

    with col1:
        prompt = st.text_area("Enter your poem prompt (up to 10 words):", height=100, max_chars=100, help="Provide a brief prompt or theme for your poem (max 10 words).")
        word_count_prompt = word_count(prompt)
        st.write(f"Word count: {word_count_prompt}/10")
        
        poet_style = st.selectbox("Choose a poet's style:", list(POET_STYLES.keys()))

    with col2:
        st.markdown("### About the Poet")
        poet_info = generate_poet_info(poet_style, selected_model)
        st.info(poet_info)

    if st.button("Generate Poem", type="primary"):
        if not prompt:
            st.warning("Please enter a prompt for your poem.")
        elif word_count_prompt > 10:
            st.warning("Please limit your prompt to 10 words or less.")
        else:
            with st.spinner("Crafting your poem..."):
                poet_data = load_poet_data(poet_style)
                if poet_data:  # Only generate if we have sample poems
                    poem = generate_poem_with_groq(prompt, poet_style, poet_data, selected_model)
                    st.success("Your poem is ready!")
                    st.markdown("### Generated Poem")
                    st.markdown(f"```\n{poem}\n```")
                else:
                    st.error("Unable to generate poem due to missing sample data.")

    # Footer
    st.markdown("---")
    st.markdown("Built with :orange_heart: thanks to Claude.ai, Groq, Github, Streamlit. :scroll: support my works at https://saweria.co/adnuri", help="cyberariani@gmail.com/081318024601")

if __name__ == "__main__":
    main()