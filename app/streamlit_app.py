import streamlit as st
import os
import sys
from urllib.parse import quote
import hashlib

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.llm.rag_pipeline import RAGPipeline


def pdf_page_link(path: str, page: int | None):
    if not os.path.exists(path):
        return None
    
    url_path = "file:///" + quote(os.path.abspath(path).replace("\\", "/"))

    if page:
        return f"{url_path}#page={page}"
    return url_path


@st.cache_resource
def load_pipeline():
    return RAGPipeline()

pipeline = load_pipeline()


st.set_page_config(
    page_title='Ассистент по документации',
    layout='wide'
)


st.title('Ассистент по технической документации')

st.markdown('Введите вопрос , основанный на технических инструкциях.')




# settings
with st.sidebar:
    st.header("Настройки")

    top_k = st.slider('Количество документов в поиске  (top_k)', 1, 10, 1)
    window = st.slider('Окно соседних чанков', 0, 10, 5)
    max_words = st.slider('Максимум слов в контексте', 300, 3000, 1500, step=100)

    st.markdown('-------------')
    st.write('Журнальные записи (debug):')
    show_debug = st.checkbox('Показать найденные документы')


question = st.text_area('Ваш вопрос: ', height=120)

if st.button('Получить ответ'):
    if not question.strip():
        st.warning('Введите вопрос!')
        st.stop()

    with st.spinner('Ищу ответ...'):
        answer, sources = pipeline.generate(question)

    st.subheader('Ответ:')
    st.write(answer)

    st.subheader("Источники")

    if not sources:
        st.write("Источников нет.")
    else:
        # Чтобы не выводить дубликаты
        seen = set()

        for i, meta in enumerate(sources):
            # безопасно извлекаем путь (поддерживаем разные ключи)
            path = meta.get("path") or meta.get("source") or meta.get("file") or None
            page = meta.get("page")
            chunk = meta.get("chunk")
            text = meta.get("text")  # если есть — покажем контекст

            # заголовок — файл или "неизвестный источник #i"
            title = os.path.basename(path) if path else f"Источник #{i+1}"

            # предотвращаем дубликаты по (path, page, chunk)
            dedup_key = f"{path}|{page}|{chunk}"
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

            with st.expander(f"📄 {title}"):
                # Показываем путь (если есть)
                if path:
                    st.markdown(f"**Полный путь:** `{path}`")
                else:
                    st.markdown("**Путь к файлу:** (не указан)")

                # Показываем номера страницы/чанка
                if page is not None:
                    st.markdown(f"**Страница:** {page}")
                if chunk is not None:
                    st.markdown(f"**Чанк:** {chunk}")

                # Показываем контекст чанка, если есть
                if text:
                    st.markdown("**Контекст:**")
                    st.write(text)

                # Кнопка скачивания — только если путь существует
                if path and os.path.exists(path):
                    try:
                        # Читаем файл в байты
                        with open(path, "rb") as f:
                            file_bytes = f.read()

                        # Формируем уникальный ключ: hash(path) + индекс
                        path_hash = hashlib.md5(path.encode("utf-8")).hexdigest()[:8]
                        download_key = f"download_{i}_{path_hash}"

                        st.download_button(
                            label="⬇️ Скачать документ",
                            data=file_bytes,
                            file_name=os.path.basename(path),
                            mime="application/pdf",
                            key=download_key
                        )
                    except Exception as e:
                        st.error(f"Не удалось открыть файл для скачивания: {e}")
                else:
                    st.info("Файл недоступен для скачивания.")
