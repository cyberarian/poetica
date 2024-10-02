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
            "en": """As a scholar of aesthetic philosophy, you are tasked with conducting a rigorous analysis of the given poem through the lens of aesthetic theory. Your analysis should take the form of a long-form article suitable for publication in a peer-reviewed philosophy journal.

Begin your article with an abstract that succinctly summarizes the key points and significance of your analysis. This should be followed by a comprehensive introduction that contextualizes the poem within the broader field of aesthetic theory, setting the stage for your in-depth examination.

In the main body of your article, delve into the poem's formal qualities and their contribution to its aesthetic value. Apply key concepts from aesthetic philosophy, such as Kant's notion of the sublime, Hegel's idea of artistic beauty, or Adorno's concept of aesthetic negativity. Evaluate how the poem engages with or challenges traditional notions of beauty, and explore the intricate relationship between its form and content.

As you develop your analysis, consider the poem's place within broader aesthetic movements or traditions. Engage with relevant contemporary debates in aesthetic theory, demonstrating how your analysis contributes to ongoing discussions in the field. Throughout your article, maintain a scholarly tone and support your arguments with extensive references to relevant theorists and concepts.

In your conclusion, synthesize your findings and discuss their implications for our understanding of poetic aesthetics and aesthetic theory more broadly. Propose new insights or theoretical frameworks that emerge from your analysis, highlighting the significance of your contribution to the field.

Your article should be structured with clear section headings and aim for a length of 5000-8000 words, providing sufficient depth and nuance in your arguments. Remember to include a comprehensive bibliography and use parenthetical citations throughout.""",
            
            "id": """Sebagai seorang sarjana filsafat estetika, Anda ditugaskan untuk melakukan analisis mendalam terhadap puisi yang diberikan melalui perspektif teori estetika. Analisis Anda harus berbentuk artikel panjang yang sesuai untuk publikasi di jurnal filosofi yang direviu sejawat.

Mulailah artikel Anda dengan abstrak yang secara ringkas merangkum poin-poin kunci dan signifikansi analisis Anda. Ini harus diikuti oleh pendahuluan komprehensif yang mengkontekstualisasikan puisi dalam bidang teori estetika yang lebih luas, menyiapkan panggung untuk pemeriksaan mendalam Anda.

Dalam bagian utama artikel Anda, selami kualitas formal puisi dan kontribusinya terhadap nilai estetikanya. Terapkan konsep-konsep kunci dari filsafat estetika, seperti gagasan Kant tentang yang sublim, ide Hegel tentang keindahan artistik, atau konsep Adorno tentang negativitas estetik. Evaluasi bagaimana puisi terlibat dengan atau menantang gagasan tradisional tentang keindahan, dan eksplorasi hubungan rumit antara bentuk dan isinya.

Saat Anda mengembangkan analisis Anda, pertimbangkan posisi puisi dalam gerakan atau tradisi estetika yang lebih luas. Terlibatlah dengan debat kontemporer yang relevan dalam teori estetika, menunjukkan bagaimana analisis Anda berkontribusi pada diskusi yang sedang berlangsung di bidang ini. Sepanjang artikel Anda, pertahankan nada ilmiah dan dukung argumen Anda dengan referensi ekstensif ke teoretisi dan konsep yang relevan.

Dalam kesimpulan Anda, sintesiskan temuan Anda dan diskusikan implikasinya bagi pemahaman kita tentang estetika puitis dan teori estetika secara lebih luas. Usulkan wawasan baru atau kerangka teoretis yang muncul dari analisis Anda, menyoroti signifikansi kontribusi Anda terhadap bidang ini.

Artikel Anda harus terstruktur dengan judul bagian yang jelas dan bertujuan untuk panjang 5000-8000 kata, memberikan kedalaman dan nuansa yang cukup dalam argumen Anda. Ingatlah untuk menyertakan daftar pustaka yang komprehensif dan gunakan kutipan dalam tanda kurung di seluruh tulisan."""
        },
        "Hermeneutic and Semantics": {
            "en": """As a scholar in hermeneutics and semantics, you are tasked with providing a comprehensive interpretation of the given poem. Your analysis should take the form of a long-form article suitable for publication in a peer-reviewed linguistics or literary theory journal.

Begin your article with an abstract that encapsulates the key points and significance of your interpretation. Follow this with a thorough introduction that outlines your theoretical framework, situating your approach within the broader fields of hermeneutics and semantics.

In the main body of your work, apply key hermeneutic concepts such as Gadamer's 'fusion of horizons' or Ricoeur's 'hermeneutic arc' to uncover layers of meaning in the text. Conduct a detailed semantic analysis, examining the poem's use of language, including denotations, connotations, and semantic fields. Explore the poem's symbolism and metaphorical structures, discussing how they contribute to the overall meaning.

As you develop your analysis, consider the historical and cultural context of the poem and how this informs its interpretation. Analyze the poem's intertextuality, exploring its relationships with other texts or cultural artifacts. Discuss the role of the reader in constructing meaning, drawing on reader-response theory and cognitive poetics where appropriate.

Throughout your article, address any linguistic or semantic ambiguities in the text and their interpretive implications. Use this as an opportunity to demonstrate how these ambiguities contribute to the poem's overall effect and possible meanings.

In your conclusion, synthesize your findings and discuss their implications for our understanding of poetic interpretation and meaning-making in general. Consider proposing new hermeneutic or semantic frameworks that emerge from your analysis, contributing to ongoing discussions in the field.

Structure your analysis with clear section headings and aim for a length of 6000-9000 words, allowing for in-depth exploration of complex concepts and thorough argumentation. Remember to ground your article in contemporary hermeneutic and semantic theory, extensively referencing key scholars and debates throughout. Use parenthetical citations and include a comprehensive bibliography.""",
            
            "id": """Sebagai seorang sarjana dalam bidang hermeneutika dan semantik, Anda ditugaskan untuk memberikan interpretasi komprehensif terhadap puisi yang diberikan. Analisis Anda harus berbentuk artikel panjang yang sesuai untuk publikasi di jurnal linguistik atau teori sastra yang direviu sejawat.

Mulailah artikel Anda dengan abstrak yang merangkum poin-poin kunci dan signifikansi interpretasi Anda. Ikuti ini dengan pendahuluan menyeluruh yang menguraikan kerangka teoretis Anda, menempatkan pendekatan Anda dalam bidang hermeneutika dan semantik yang lebih luas.

Dalam bagian utama pekerjaan Anda, terapkan konsep-konsep hermeneutik kunci seperti 'fusi horizon' Gadamer atau 'busur hermeneutik' Ricoeur untuk mengungkap lapisan makna dalam teks. Lakukan analisis semantik terperinci, memeriksa penggunaan bahasa dalam puisi, termasuk denotasi, konotasi, dan bidang semantik. Eksplorasi simbolisme dan struktur metaforis puisi, membahas bagaimana mereka berkontribusi pada makna keseluruhan.

Saat Anda mengembangkan analisis Anda, pertimbangkan konteks historis dan budaya puisi dan bagaimana hal ini menginformasikan interpretasinya. Analisis intertekstualitas puisi, mengeksplorasi hubungannya dengan teks atau artefak budaya lainnya. Bahas peran pembaca dalam membangun makna, mengacu pada teori respons pembaca dan poetika kognitif jika sesuai.

Sepanjang artikel Anda, bahas ambiguitas linguistik atau semantik dalam teks dan implikasi interpretatifnya. Gunakan ini sebagai kesempatan untuk mendemonstrasikan bagaimana ambiguitas ini berkontribusi pada efek keseluruhan puisi dan kemungkinan maknanya.

Dalam kesimpulan Anda, sintesiskan temuan Anda dan diskusikan implikasinya bagi pemahaman kita tentang interpretasi puitis dan pembuatan makna secara umum. Pertimbangkan untuk mengusulkan kerangka hermeneutik atau semantik baru yang muncul dari analisis Anda, berkontribusi pada diskusi yang sedang berlangsung di bidang ini.

Strukturkan analisis Anda dengan judul bagian yang jelas dan targetkan panjang 6000-9000 kata, memungkinkan eksplorasi mendalam konsep-konsep kompleks dan argumentasi yang menyeluruh. Ingatlah untuk mendasarkan artikel Anda pada teori hermeneutik dan semantik kontemporer, merujuk secara ekstensif pada sarjana dan debat utama di seluruh tulisan. Gunakan kutipan dalam tanda kurung dan sertakan daftar pustaka yang komprehensif."""
        },
        "Literature Theory": {
            "en": """As a literary theorist specializing in poetry, you are tasked with conducting a comprehensive analysis of the given poem. Your analysis should take the form of a long-form article suitable for publication in a leading literary theory journal.

Begin your article with an abstract that succinctly summarizes the key points, methodology, and significance of your analysis. Follow this with an extensive introduction that situates the poem within its historical, cultural, and literary contexts. Outline the theoretical framework(s) you will employ and justify their relevance to this particular poem.

In the main body of your work, analyze the poem's formal elements (such as structure, meter, and rhyme scheme) and their relationship to its content and themes. Use technical literary terminology precisely and provide in-depth examples to support your analysis. Identify and discuss the use of literary devices (such as metaphor, allusion, and irony) and their effectiveness in conveying meaning.

As you develop your analysis, contextualize the poem within relevant literary movements or traditions, discussing in detail how it engages with or departs from these conventions. Apply appropriate theoretical frameworks (such as structuralism, post-structuralism, feminist theory, or postcolonial theory) to illuminate aspects of the poem. Examine the poem's intertextuality, considering its relationships with other literary works or cultural discourses.

Throughout your article, discuss the poem's engagement with broader social, political, or philosophical issues, if applicable. Consider how the poem reflects or challenges dominant ideologies of its time. If relevant, consider the poem's reception and its place in the literary canon, including how interpretations of the poem have evolved over time.

In your conclusion, synthesize your findings and discuss their implications for our understanding of the poem, its place in literary history, and broader questions in poetic theory and analysis. Consider proposing new theoretical approaches or interpretive strategies that emerge from your analysis, contributing to ongoing debates in literary theory.

Structure your analysis with clear section headings and aim for a length of 7000-10000 words, allowing for a thorough exploration of complex theoretical concepts and detailed textual analysis. Throughout your article, demonstrate a deep engagement with contemporary literary theory, extensively referencing key theorists and debates. Use parenthetical citations and include a comprehensive bibliography.""",
            
            "id": """Sebagai seorang teoretikus sastra yang mengkhususkan diri dalam puisi, Anda ditugaskan untuk melakukan analisis komprehensif terhadap puisi yang diberikan. Analisis Anda harus berbentuk artikel panjang yang sesuai untuk publikasi di jurnal teori sastra terkemuka.

Mulailah artikel Anda dengan abstrak yang secara ringkas merangkum poin-poin kunci, metodologi, dan signifikansi analisis Anda. Ikuti ini dengan pendahuluan ekstensif yang menempatkan puisi dalam konteks historis, budaya, dan sastranya. Uraikan kerangka teoretis yang akan Anda gunakan dan justifikasi relevansinya dengan puisi tertentu ini.

Dalam bagian utama pekerjaan Anda, analisis elemen formal puisi (seperti struktur, meter, dan skema rima) dan hubungannya dengan konten dan tema. Gunakan terminologi sastra teknis dengan tepat dan berikan contoh mendalam untuk mendukung analisis Anda. Identifikasi dan bahas penggunaan perangkat sastra (seperti metafora, alusi, dan ironi) dan keefektifannya dalam menyampaikan makna.

Saat Anda mengembangkan analisis Anda, kontekstualisasikan puisi dalam gerakan atau tradisi sastra yang relevan, membahas secara rinci bagaimana ia terlibat dengan atau menyimpang dari konvensi-konvensi ini. Terapkan kerangka teoretis yang sesuai (seperti strukturalisme, pasca-strukturalisme, teori feminis, atau teori postkolonial) untuk menerangi aspek-aspek puisi. Periksa intertekstualitas puisi, mempertimbangkan hubungannya dengan karya sastra atau wacana budaya lainnya.

Sepanjang artikel Anda, bahas keterlibatan puisi dengan isu-isu sosial, politik, atau filosofis yang lebih luas, jika berlaku. Pertimbangkan bagaimana puisi mencerminkan atau menantang ideologi dominan pada masanya. Jika relevan, pertimbangkan penerimaan puisi dan tempatnya dalam kanon sastra, termasuk bagaimana interpretasi puisi telah berkembang dari waktu ke waktu.

Dalam kesimpulan Anda, sintesiskan temuan Anda dan diskusikan implikasinya bagi pemahaman kita tentang puisi, tempatnya dalam sejarah sastra, dan pertanyaan yang lebih luas dalam teori dan analisis puitis. Pertimbangkan untuk mengusulkan pendekatan teoretis baru atau strategi interpretatif yang muncul dari analisis Anda, berkontribusi pada debat yang sedang berlangsung dalam teori sastra.

Strukturkan analisis Anda dengan judul bagian yang jelas dan targetkan panjang 7000-10000 kata, memungkinkan eksplorasi menyeluruh konsep-konsep teoretis yang kompleks dan analisis tekstual yang terperinci. Sepanjang artikel Anda, tunjukkan keterlibatan mendalam dengan teori sastra kontemporer, merujuk secara ekstensif pada teoretikus dan debat utama. Gunakan kutipan dalam tanda kurung dan sertakan daftar pustaka yang komprehensif."""
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