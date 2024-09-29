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
    "Sutardji Calzoum Bachri": "Mantra-like, playful language, existential themes, rhythmic repetition, cultural identity, reflect a deep exploration of sound, meaning, and the spiritual dimensions of existence, while also challenging conventional forms and embracing "
}

GROQ_MODELS = [
    "llama-3.2-90b-text-preview",
    "llama-3.2-11b-text-preview",
    "llama-3.2-3b-preview",
    "llama-3.1-70b-versatile",
    "llama-3.1-8b-instant",
    "gemma2-9b-it",
    "gemma-7b-it",
    "llama3-groq-70b-8192-tool-use-preview",
    "llama3-groq-8b-8192-tool-use-preview",
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
            "en": """As a scholar of aesthetic philosophy, conduct a rigorous analysis of the given poem through the lens of aesthetic theory. Your analysis should:

1. Examine the poem's formal qualities (e.g., structure, rhythm, imagery) and their contribution to its aesthetic value.
2. Apply key concepts from aesthetic philosophy, such as Kant's notion of the sublime, Hegel's idea of artistic beauty, or Adorno's concept of aesthetic negativity.
3. Evaluate the poem's sensory and emotional impact, considering how it engages with or challenges traditional notions of beauty.
4. Discuss the relationship between form and content, exploring how the poem's aesthetic choices inform its meaning.
5. Consider the poem's place within broader aesthetic movements or traditions.
6. Engage with relevant contemporary debates in aesthetic theory as they pertain to the poem.

Your analysis should be scholarly in tone, referencing relevant theorists and concepts where appropriate, and should aim to contribute to ongoing discussions in the field of aesthetic philosophy.""",
            
            "id": """Sebagai seorang sarjana filsafat estetika, lakukan analisis mendalam terhadap puisi yang diberikan melalui perspektif teori estetika. Analisis Anda harus:

1. Memeriksa kualitas formal puisi (misalnya, struktur, ritme, citra) dan kontribusinya terhadap nilai estetikanya.
2. Menerapkan konsep-konsep kunci dari filsafat estetika, seperti gagasan Kant tentang yang sublim, ide Hegel tentang keindahan artistik, atau konsep Adorno tentang negativitas estetik.
3. Mengevaluasi dampak sensorik dan emosional puisi, mempertimbangkan bagaimana ia terlibat dengan atau menantang gagasan tradisional tentang keindahan.
4. Membahas hubungan antara bentuk dan isi, mengeksplorasi bagaimana pilihan estetika puisi menginformasikan maknanya.
5. Mempertimbangkan posisi puisi dalam gerakan atau tradisi estetika yang lebih luas.
6. Terlibat dengan debat kontemporer yang relevan dalam teori estetika sejauh berkaitan dengan puisi tersebut.

Analisis Anda harus bernada ilmiah, merujuk pada teoretisi dan konsep yang relevan bila sesuai, dan harus bertujuan untuk berkontribusi pada diskusi yang sedang berlangsung di bidang filsafat estetika."""
        },
        "Hermeneutic and Semantics": {
            "en": """As a scholar in hermeneutics and semantics, provide a comprehensive interpretation of the given poem. Your analysis should:

1. Apply key hermeneutic concepts, such as Gadamer's 'fusion of horizons' or Ricoeur's 'hermeneutic arc', to uncover layers of meaning in the text.
2. Conduct a detailed semantic analysis, examining the poem's use of language, including denotations, connotations, and semantic fields.
3. Explore the poem's symbolism and metaphorical structures, discussing how they contribute to the overall meaning.
4. Consider the historical and cultural context of the poem, and how this informs its interpretation.
5. Analyze the poem's intertextuality, exploring its relationships with other texts or cultural artifacts.
6. Discuss the role of the reader in constructing meaning, drawing on reader-response theory where appropriate.
7. Address any linguistic or semantic ambiguities in the text and their interpretive implications.

Your analysis should be grounded in contemporary hermeneutic and semantic theory, referencing key scholars and debates in the field. Aim to provide insights that contribute to our understanding of how meaning is constructed and interpreted in poetic texts.""",
            
            "id": """Sebagai seorang sarjana dalam bidang hermeneutika dan semantik, berikan interpretasi komprehensif terhadap puisi yang diberikan. Analisis Anda harus:

1. Menerapkan konsep-konsep hermeneutik kunci, seperti 'fusi horizon' Gadamer atau 'busur hermeneutik' Ricoeur, untuk mengungkap lapisan makna dalam teks.
2. Melakukan analisis semantik terperinci, memeriksa penggunaan bahasa dalam puisi, termasuk denotasi, konotasi, dan bidang semantik.
3. Mengeksplorasi simbolisme dan struktur metaforis puisi, membahas bagaimana mereka berkontribusi pada makna keseluruhan.
4. Mempertimbangkan konteks historis dan budaya puisi, dan bagaimana hal ini menginformasikan interpretasinya.
5. Menganalisis intertekstualitas puisi, mengeksplorasi hubungannya dengan teks atau artefak budaya lainnya.
6. Membahas peran pembaca dalam membangun makna, mengacu pada teori respons pembaca jika sesuai.
7. Membahas ambiguitas linguistik atau semantik dalam teks dan implikasi interpretatifnya.

Analisis Anda harus didasarkan pada teori hermeneutik dan semantik kontemporer, merujuk pada sarjana dan debat utama di bidang ini. Berusahalah untuk memberikan wawasan yang berkontribusi pada pemahaman kita tentang bagaimana makna dibangun dan ditafsirkan dalam teks puitis."""
        },
        "Literature Theory": {
            "en": """As a literary theorist specializing in poetry, conduct a comprehensive analysis of the given poem. Your examination should:

1. Analyze the poem's formal elements (e.g., structure, meter, rhyme scheme) and their relationship to its content and themes.
2. Identify and discuss the use of literary devices (e.g., metaphor, allusion, irony) and their effectiveness in conveying meaning.
3. Contextualize the poem within relevant literary movements or traditions, discussing how it engages with or departs from these conventions.
4. Apply appropriate theoretical frameworks (e.g., structuralism, post-structuralism, feminist theory) to illuminate aspects of the poem.
5. Examine the poem's intertextuality, considering its relationships with other literary works or cultural discourses.
6. Discuss the poem's engagement with broader social, political, or philosophical issues, if applicable.
7. Consider the poem's reception and its place in the literary canon, if relevant.

Your analysis should demonstrate a deep engagement with contemporary literary theory, referencing key theorists and debates where appropriate. Aim to provide insights that contribute to our understanding of the poem and its significance within the broader context of literary studies.""",
            
            "id": """Sebagai seorang teoretikus sastra yang mengkhususkan diri dalam puisi, lakukan analisis komprehensif terhadap puisi yang diberikan. Pemeriksaan Anda harus:

1. Menganalisis elemen formal puisi (misalnya, struktur, meter, skema rima) dan hubungannya dengan konten dan tema.
2. Mengidentifikasi dan membahas penggunaan perangkat sastra (misalnya, metafora, alusi, ironi) dan keefektifannya dalam menyampaikan makna.
3. Mengontekstualisasikan puisi dalam gerakan atau tradisi sastra yang relevan, membahas bagaimana ia terlibat dengan atau menyimpang dari konvensi-konvensi ini.
4. Menerapkan kerangka teoretis yang sesuai (misalnya, strukturalisme, pasca-strukturalisme, teori feminis) untuk menerangi aspek-aspek puisi.
5. Memeriksa intertekstualitas puisi, mempertimbangkan hubungannya dengan karya sastra atau wacana budaya lainnya.
6. Membahas keterlibatan puisi dengan isu-isu sosial, politik, atau filosofis yang lebih luas, jika berlaku.
7. Mempertimbangkan penerimaan puisi dan tempatnya dalam kanon sastra, jika relevan.

Analisis Anda harus menunjukkan keterlibatan mendalam dengan teori sastra kontemporer, merujuk pada teoretikus dan debat utama jika sesuai. Berusahalah untuk memberikan wawasan yang berkontribusi pada pemahaman kita tentang puisi dan signifikansinya dalam konteks studi sastra yang lebih luas."""
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