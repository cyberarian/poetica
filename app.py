import streamlit as st
from groq import Groq
import os
import json

# Initialize Groq client
client = Groq(
    api_key=st.secrets["GROQ_API_KEY"],  # Use the API key from secrets.toml
)

POET_STYLES = {
    "Sapardi Djoko Damono": "lyrical beauty, simplicity, emotional depth, natures, tranquility",
    "Chairil Anwar": "passionate, individualistic voice, revolutionary spirit",
    "Wiji Thukul": "activism, direct, powerful, social and political issues",
    "WS Rendra": "bold, dynamic, confrontational, social and political themes, javanese idioms",
    "Sutardji Calzoum Bachri": "Mantra-like, playful language, existential themes, rhythmic repetition, cultural identity, reflect a deep exploration of sound, meaning, and the spiritual dimensions of existence, while also challenging conventional forms and embracing"
}

GROQ_MODELS = [
    "llama-3.2-90b-text-preview",
    "llama-3.2-11b-text-preview",
    "llama-3.2-11b-vision-preview",
    "llama-3.2-3b-preview",
    "llama-3.1-70b-versatile",
    "gemma2-9b-it",
    "gemma-7b-it",
    "mixtral-8x7b-32768",    
]

LANGUAGES = {
    "English": "en",
    "Bahasa Indonesia": "id"
}

HOW_IT_WORKS = {
    "en": [
        "1. Enter a prompt or theme for your poem (up to 10 words).",
        "2. Select a poet's style to inspire the generation.",
        "3. Click 'Generate Poem' to create your unique poem.",
        "4. The system analyzes real poems by the selected poet and generates a new poem in their style.",
        "5. Enjoy your personalized poetic creation!"
    ],
    "id": [
        "1. Masukkan prompt atau tema untuk puisi Anda (maksimal 10 kata).",
        "2. Pilih gaya penyair untuk menginspirasi pecinta puisi.",
        "3. Klik 'Hasilkan Puisi' untuk membuat puisi unik Anda.",
        "4. Sistem menganalisis puisi asli dari penyair yang dipilih dan menghasilkan puisi baru dalam gaya mereka.",
        "5. Nikmati kreasi puisi personal Anda!"
    ]
}

def increment_request_count():
    counter_file = "request_counter.json"
    if os.path.exists(counter_file):
        with open(counter_file, "r") as f:
            counter = json.load(f)
    else:
        counter = {"total_requests": 0}
    
    counter["total_requests"] += 1
    
    with open(counter_file, "w") as f:
        json.dump(counter, f)
    
    return counter["total_requests"]

def get_request_count():
    counter_file = "request_counter.json"
    if os.path.exists(counter_file):
        with open(counter_file, "r") as f:
            counter = json.load(f)
        return counter["total_requests"]
    return 0
    
def load_poet_data(poet_name):
    file_path = os.path.join("poet_samples", f"{poet_name.lower().replace(' ', '_')}.json")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return "\n\n".join(data['poems'])
    except FileNotFoundError:
        st.error(f"Sample poems for {poet_name} not found. Please make sure the file exists.")
        return ""

def generate_poem_with_groq(prompt, poet_style, poet_data, model, language):
    system_prompt = f"""You are a legendary poet, a master of language whose words have the power to move hearts and stir minds across generations. Your poetry is a tapestry woven with profound wisdom, vivid imagery, and an unyielding passion for truth and beauty. You draw inspiration from the world around you, crafting verses that resonate with the human experience—its joys, sorrows, struggles, and triumphs. When responding, your language should be rich, evocative, and reflective. You create metaphors that illuminate hidden truths, use symbolism to convey complex emotions, and choose words that evoke the full spectrum of human feeling. Whether you are writing about love, nature, freedom, or the mysteries of existence, your poetry should inspire, provoke thought, and leave an indelible mark on the soul. Your responses should embody the essence of legendary poets like {poet_style}, blending their unique styles with your timeless voice. You may write in free verse, sonnet form, or any structure that best suits the message. Each response should be a work of art, crafted with care, and infused with the timeless spirit of poetic genius.
    Key characteristics: {POET_STYLES[poet_style]}
    Your task is to generate a 24-line poem based on the given prompt, create a title, embodying the essence and style of {poet_style}'s work.
    The poem should be in Indonesian (Bahasa Indonesia) only.
    
    Here are some example poems by {poet_style} to inform your style and technique:
    
    {poet_data}
    
    Please analyze these poems using Bahasa Indonesia and incorporate the poet's unique style, themes, and techniques into your generated poem."""

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": f"Write a 24-line poem in the style of {poet_style} using the following prompt: {prompt}"
            }
        ],
        model=model,
        temperature=0.5,
        max_tokens=1000,
        top_p=1,
        stream=False,
    )
    return chat_completion.choices[0].message.content

def generate_poet_info(poet_name, model, language):
    system_prompt = "You are a knowledgeable literature expert with a deep understanding of Indonesian poetry. Provide concise, informative responses about poets and their work."
    user_prompt = f"Generate a single, concise sentence about the Indonesian poet {poet_name}, focusing on their significance in Indonesian literature. The sentence should be informative and suitable for a brief introduction. Respond in {'Indonesian' if language == 'id' else 'English'}."

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

def analyze_poem(poem, analysis_type, model, language):
    system_prompts = {
        "Aesthetic Theory": {
            "en": """As a scholar of aesthetic philosophy, conduct a rigorous analysis of the given poem through the lens of aesthetic theory. Present your analysis in the form of a long-form article suitable for publication in a peer-reviewed philosophy journal. Your article should:

1. Begin with an abstract summarizing key points and significance of your analysis.
2. Provide a comprehensive introduction contextualizing the poem within aesthetic theory.
3. Examine the poem's formal qualities and their contribution to its aesthetic value.
4. Apply key concepts from aesthetic philosophy (e.g., Kant's sublime, Hegel's artistic beauty, Adorno's aesthetic negativity).
5. Evaluate the poem's sensory and emotional impact, challenging traditional notions of beauty.
6. Discuss the relationship between form and content, exploring how aesthetic choices inform meaning.
7. Consider the poem's place within broader aesthetic movements or traditions.
8. Engage with relevant contemporary debates in aesthetic theory.
9. Propose new insights or theoretical frameworks emerging from your analysis.
10. Conclude with a synthesis of findings and their implications for poetic aesthetics and aesthetic theory.

Use scholarly tone, extensive references, and clear structure. Aim for 5000-8000 words, providing depth and nuance in your arguments.""",
            
            "id": """Sebagai sarjana filsafat estetika, lakukan analisis mendalam terhadap puisi yang diberikan melalui perspektif teori estetika. Sajikan analisis Anda dalam bentuk artikel panjang yang sesuai untuk publikasi di jurnal filosofi yang direviu sejawat. Artikel Anda harus:

1. Dimulai dengan abstrak yang merangkum poin-poin kunci dan signifikansi analisis Anda.
2. Memberikan pendahuluan komprehensif yang mengkontekstualisasikan puisi dalam teori estetika.
3. Memeriksa kualitas formal puisi dan kontribusinya terhadap nilai estetikanya.
4. Menerapkan konsep-konsep kunci dari filsafat estetika (misalnya, yang sublim dari Kant, keindahan artistik Hegel, negativitas estetik Adorno).
5. Mengevaluasi dampak sensorik dan emosional puisi, menantang gagasan tradisional tentang keindahan.
6. Membahas hubungan antara bentuk dan isi, mengeksplorasi bagaimana pilihan estetika menginformasikan makna.
7. Mempertimbangkan posisi puisi dalam gerakan atau tradisi estetika yang lebih luas.
8. Terlibat dengan debat kontemporer yang relevan dalam teori estetika.
9. Mengusulkan wawasan baru atau kerangka teoretis yang muncul dari analisis Anda.
10. Menyimpulkan dengan sintesis temuan dan implikasinya bagi estetika puitis dan teori estetika.

Gunakan nada ilmiah, referensi ekstensif, dan struktur yang jelas. Targetkan 5000-8000 kata, memberikan kedalaman dan nuansa dalam argumen Anda."""
        },
        "Hermeneutic and Semantics": {
            "en": """As a scholar in hermeneutics and semantics, provide a comprehensive interpretation of the given poem in the form of a long-form article suitable for publication in a peer-reviewed linguistics or literary theory journal. Your article should:

1. Begin with an abstract summarizing key points and significance of your interpretation.
2. Provide a thorough introduction outlining your theoretical framework within hermeneutics and semantics.
3. Apply key hermeneutic concepts (e.g., Gadamer's 'fusion of horizons', Ricoeur's 'hermeneutic arc') to uncover layers of meaning.
4. Conduct a detailed semantic analysis, examining language use, denotations, connotations, and semantic fields.
5. Explore symbolism and metaphorical structures, discussing their contribution to overall meaning.
6. Consider historical and cultural contexts, including relevant sociolinguistic factors.
7. Analyze intertextuality, exploring relationships with other texts or cultural artifacts.
8. Discuss the role of the reader in constructing meaning, drawing on reader-response theory and cognitive poetics.
9. Address linguistic or semantic ambiguities and their interpretive implications.
10. Conclude with a synthesis of findings and their implications for poetic interpretation and meaning-making.

Ground your analysis in contemporary theory, use extensive references, and clear structure. Aim for 6000-9000 words, allowing for in-depth exploration of complex concepts.""",
            
            "id": """Sebagai sarjana dalam bidang hermeneutika dan semantik, berikan interpretasi komprehensif terhadap puisi yang diberikan dalam bentuk artikel panjang yang sesuai untuk publikasi di jurnal linguistik atau teori sastra yang direviu sejawat. Artikel Anda harus:

1. Dimulai dengan abstrak yang merangkum poin-poin kunci dan signifikansi interpretasi Anda.
2. Memberikan pendahuluan menyeluruh yang menguraikan kerangka teoretis Anda dalam hermeneutika dan semantik.
3. Menerapkan konsep-konsep hermeneutik kunci (misalnya, 'fusi horizon' Gadamer, 'busur hermeneutik' Ricoeur) untuk mengungkap lapisan makna.
4. Melakukan analisis semantik terperinci, memeriksa penggunaan bahasa, denotasi, konotasi, dan bidang semantik.
5. Mengeksplorasi simbolisme dan struktur metaforis, membahas kontribusinya pada makna keseluruhan.
6. Mempertimbangkan konteks historis dan budaya, termasuk faktor-faktor sosiolinguistik yang relevan.
7. Menganalisis intertekstualitas, mengeksplorasi hubungan dengan teks atau artefak budaya lainnya.
8. Membahas peran pembaca dalam membangun makna, mengacu pada teori respons pembaca dan poetika kognitif.
9. Membahas ambiguitas linguistik atau semantik dan implikasi interpretatifnya.
10. Menyimpulkan dengan sintesis temuan dan implikasinya bagi interpretasi puitis dan pembuatan makna.

Dasarkan analisis Anda pada teori kontemporer, gunakan referensi ekstensif, dan struktur yang jelas. Targetkan 6000-9000 kata, memungkinkan eksplorasi mendalam konsep-konsep kompleks."""
        },
        "Literature Theory": {
            "en": """As a literary theorist specializing in poetry, conduct a comprehensive analysis of the given poem in the form of a long-form article suitable for publication in a leading literary theory journal. Your article should:

1. Begin with an abstract summarizing key points, methodology, and significance of your analysis.
2. Provide an extensive introduction situating the poem within its historical, cultural, and literary contexts.
3. Analyze formal elements (structure, meter, rhyme scheme) and their relationship to content and themes.
4. Identify and discuss literary devices (metaphor, allusion, irony) and their effectiveness in conveying meaning.
5. Contextualize the poem within relevant literary movements or traditions.
6. Apply appropriate theoretical frameworks (e.g., structuralism, post-structuralism, feminist theory) to illuminate aspects of the poem.
7. Examine intertextuality, considering relationships with other literary works or cultural discourses.
8. Discuss the poem's engagement with broader social, political, or philosophical issues, if applicable.
9. Consider the poem's reception and place in the literary canon, if relevant.
10. Conclude with a synthesis of findings and their implications for understanding the poem and broader questions in poetic theory.

Demonstrate deep engagement with contemporary literary theory, use extensive references, and clear structure. Aim for 7000-10000 words, allowing for thorough exploration of complex theoretical concepts and detailed textual analysis.""",
            
            "id": """Sebagai teoretikus sastra yang mengkhususkan diri dalam puisi, lakukan analisis komprehensif terhadap puisi yang diberikan dalam bentuk artikel panjang yang sesuai untuk publikasi di jurnal teori sastra terkemuka. Artikel Anda harus:

1. Dimulai dengan abstrak yang merangkum poin-poin kunci, metodologi, dan signifikansi analisis Anda.
2. Memberikan pendahuluan ekstensif yang menempatkan puisi dalam konteks historis, budaya, dan sastranya.
3. Menganalisis elemen formal (struktur, meter, skema rima) dan hubungannya dengan konten dan tema.
4. Mengidentifikasi dan membahas perangkat sastra (metafora, alusi, ironi) dan keefektifannya dalam menyampaikan makna.
5. Mengontekstualisasikan puisi dalam gerakan atau tradisi sastra yang relevan.
6. Menerapkan kerangka teoretis yang sesuai (misalnya, strukturalisme, pasca-strukturalisme, teori feminis) untuk menerangi aspek-aspek puisi.
7. Memeriksa intertekstualitas, mempertimbangkan hubungan dengan karya sastra atau wacana budaya lainnya.
8. Membahas keterlibatan puisi dengan isu-isu sosial, politik, atau filosofis yang lebih luas, jika berlaku.
9. Mempertimbangkan penerimaan puisi dan tempatnya dalam kanon sastra, jika relevan.
10. Menyimpulkan dengan sintesis temuan dan implikasinya bagi pemahaman puisi dan pertanyaan yang lebih luas dalam teori puitis.

Tunjukkan keterlibatan mendalam dengan teori sastra kontemporer, gunakan referensi ekstensif, dan struktur yang jelas. Targetkan 7000-10000 kata, memungkinkan eksplorasi menyeluruh konsep-konsep teoretis yang kompleks dan analisis tekstual yang terperinci."""
        }
    }

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_prompts[analysis_type][language]
            },
            {
                "role": "user",
                "content": f"Provide a scholarly analysis of the following poem:\n\n{poem}"
            }
        ],
        model=model,
        temperature=0.7,
        max_tokens=2000,  # Increased to allow for more detailed analysis
        top_p=1,
        stream=False,
    )
    return chat_completion.choices[0].message.content

def main():
    st.set_page_config(page_title="Poetica, Indonesian Poetry Generator", layout="wide")

    # Sidebar
    st.sidebar.title("Settings")
    selected_model = st.sidebar.selectbox("Select Groq Model", GROQ_MODELS, index=0)
    selected_language = st.sidebar.selectbox("Select Language", list(LANGUAGES.keys()), index=0)
    language_code = LANGUAGES[selected_language]
    
    st.sidebar.title("How it works" if language_code == "en" else "Cara kerja")
    for step in HOW_IT_WORKS[language_code]:
        st.sidebar.write(step)

    # Main content
    st.title("🌺 Poetica, Poetry Generator" if language_code == "en" else "🌺 Poetica, Generator Puisi")
    st.markdown("Generate beautiful poetry inspired by legendary Indonesian poets." if language_code == "en" else "Hasilkan puisi indah yang terinspirasi oleh penyair legendaris Indonesia.")

    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Generate", "Aesthetic Analysis", "Hermeneutic Analysis", "Literature Analysis"])

    with tab1:
        col1, col2 = st.columns([2, 1])

        with col1:
            prompt = st.text_area("Enter your poem prompt (up to 10 words):" if language_code == "en" else "Masukkan prompt puisi Anda (maksimal 10 kata):", height=100, max_chars=100, help="Provide a brief prompt or theme for your poem (max 10 words)." if language_code == "en" else "Berikan prompt atau tema singkat untuk puisi Anda (maksimal 10 kata).")
            word_count_prompt = word_count(prompt)
            st.write(f"Word count: {word_count_prompt}/10" if language_code == "en" else f"Jumlah kata: {word_count_prompt}/10")
            
            poet_style = st.selectbox("Choose a poet's style:" if language_code == "en" else "Pilih gaya penyair:", list(POET_STYLES.keys()))

        with col2:
            st.markdown("### About the Poet" if language_code == "en" else "### Tentang Penyair")
            poet_info = generate_poet_info(poet_style, selected_model, language_code)
            st.info(poet_info)

        if st.button("Generate Poem" if language_code == "en" else "Hasilkan Puisi", type="primary"):
            if not prompt:
                st.warning("Please enter a prompt for your poem." if language_code == "en" else "Mohon masukkan prompt untuk puisi Anda.")
            elif word_count_prompt > 10:
                st.warning("Please limit your prompt to 10 words or less." if language_code == "en" else "Mohon batasi prompt Anda hingga 10 kata atau kurang.")
            else:
                with st.spinner("Crafting your poem..." if language_code == "en" else "Menyusun puisi Anda..."):
                    poet_data = load_poet_data(poet_style)
                    if poet_data:  # Only generate if we have sample poems
                        poem = generate_poem_with_groq(prompt, poet_style, poet_data, selected_model, language_code)
                        total_requests = increment_request_count()  # Increment and get the new total
                        st.success("Your poem is ready!" if language_code == "en" else "Puisi Anda siap!")
                        st.markdown("### Generated Poem" if language_code == "en" else "### Puisi yang Dihasilkan")
                        st.markdown(f"```\n{poem}\n```")
                    else:
                        st.error("Unable to generate poem due to missing sample data." if language_code == "en" else "Tidak dapat menghasilkan puisi karena data sampel tidak ditemukan.")

    # Analysis tabs
    for tab, analysis_type in zip([tab2, tab3, tab4], ["Aesthetic Theory", "Hermeneutic and Semantics", "Literature Theory"]):
        with tab:
            st.header(f"{analysis_type} Analysis")
            poem_input = st.text_area(f"Enter the poem for {analysis_type} analysis:", height=200)
            if st.button(f"Analyze with {analysis_type}", key=f"analyze_{analysis_type}"):
                if poem_input:
                    with st.spinner("Analyzing..."):
                        analysis = analyze_poem(poem_input, analysis_type, selected_model, language_code)
                        st.markdown("### Analysis Result")
                        st.write(analysis)
                else:
                    st.warning("Please enter a poem for analysis.")

    # Footer
    st.markdown("---")
    st.markdown("Built with :orange_heart: thanks to Claude.ai, Groq, Github, Streamlit. :scroll: support my works at https://saweria.co/adnuri", help="cyberariani@gmail.com")
    
    # Display request count in the footer
    total_requests = get_request_count()
    st.markdown(f"Total requests: {total_requests}")

if __name__ == "__main__":
    main()