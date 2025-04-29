import streamlit as st
import json
import requests
from io import BytesIO
from openai import OpenAI
from dotenv import dotenv_values

def is_valid_api_key(api_key):
    try:
        client = OpenAI(api_key=api_key)
        client.models.list()  # Próba dostępu do modeli
        return True
    except Exception:
        return False

# Inicjalizacja stanu sesji
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title(":rainbow: Matejko")
    api_key_input = st.text_input("Wprowadź swój klucz OpenAI:", type="password")
    if st.button("Zaloguj"):
        if is_valid_api_key(api_key_input):
            st.session_state.authenticated = True
            st.session_state.api_key = api_key_input
            st.success("Zalogowano!")
            st.rerun()
        else:
            st.error("Nieprawidłowy klucz API. Spróbuj ponownie.")
    st.stop()

env = dotenv_values(".env")
openai_client = OpenAI(api_key=env["OPENAI_API_KEY"])

st.title(':rainbow: Matejko')

if "ideas" not in st.session_state:
    st.session_state.ideas = None
if "selected_idea" not in st.session_state:
    st.session_state.selected_idea = None


def generator_pomysłów(temat):
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Jesteś kreatywnym pomocnikiem, który wymyśla pomysły na kolorowanki na podany temat."},
            {"role": "user", "content": f"Wygeneruj 5 prostych pomysłów na kolorowanki dla dzieci związane z: {temat}."}
        ]
    )
    pomysły = response.choices[0].message.content.strip().split("\n")
    return pomysły


def generator_images(pomysł, liczba):
    images = []
    for _ in range(liczba):
        response = openai_client.images.generate(
            model="dall-e-3",
            prompt=f"kolorowanka: białe tło, czarne linie, dostosowane dla dzieci: {pomysł}",
            n=1,
            size="1024x1024",
            quality="standard"
        )
        images.append(response.data[0].url)
    return images


# Nowa funkcjonalność: Generowanie opowiadania
def generator_opowiadania(pomysł):
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Jesteś kreatywnym pomocnikiem, który tworzy opowiadania dla dzieci."},
            {"role": "user", "content": f"Stwórz krótkie, kreatywne opowiadanie o kolorowance na temat: {pomysł}."}
        ]
    )
    opowiadanie = response.choices[0].message.content.strip()
    return opowiadanie


temat = st.text_input('Wpisz temat kolorowanki')

if st.button(':brain: Generuj pomysły'):
    with st.spinner("Generowanie pomysłów"):
        st.session_state.ideas = generator_pomysłów(temat)

if st.session_state.ideas:
    # Lokalna zmienna dla wygody
    ideas = st.session_state.ideas

    # Wybór pomysłu
    selected_idea = st.selectbox("Wybierz pomysł na kolorowankę:", ideas)
    st.session_state.selected_idea = selected_idea

    # Generowanie opowiadania
    if st.button('📖 Generuj opowiadanie do kolorowanki'):
        with st.spinner('Generowanie opowiadania'):
            story = generator_opowiadania(selected_idea)
            st.write("**Opowiadanie do kolorowanki:**")
            st.write(story)

    # Liczba kolorowanek
    liczba = st.slider('Liczba kolorowanek', 1, 5, 1)

    # Kliknięcie przycisku
    if st.button('🎨 Wygeneruj kolorowanki'):
        if selected_idea:
            with st.spinner('Generowanie kolorowanek'):
                images = generator_images(selected_idea, liczba)

            # Wyświetlenie obrazów + przyciski pobierania
            for i, image_url in enumerate(images):
                st.write(f"**Kolorowanka {i+1}:** {selected_idea}")
                st.image(image_url, caption=f"Kolorowanka {i+1}")

                response = requests.get(image_url)
                image_bytes = BytesIO(response.content)

                st.download_button(
                    label=f"Pobierz kolorowankę {i+1}",
                    data=image_bytes,
                    file_name=f"kolorowanka_{i+1}.png",
                    mime="image/png"
                )
