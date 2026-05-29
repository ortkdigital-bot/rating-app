import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Рейтинг 4.5+", layout="wide")
st.title("🚀 Автоматизация отбора артикулов для отзывов")
st.caption("Цель: 4.5+ на всех площадках")

uploaded_file = st.file_uploader("Загрузи Excel-отчёт от аналитики", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.columns = [str(col).strip() for col in df.columns]

    # Автоматический поиск нужных колонок
    def find_col(keywords):
        for col in df.columns:
            if any(kw.lower() in str(col).lower() for kw in keywords):
                return col
        return None

    platform_col = find_col(['Площадка']) or 'Площадка'
    status_col = find_col(['Статус']) or 'Статус'
    name_col = find_col(['Наименование', 'Название']) or 'Наименование'
    rating_col = find_col(['Рейтинг']) or 'Рейтинг'
    reviews_col = find_col(['Кол-во отзывов', 'Отзывов']) or 'Кол-во отзывов'
    prev_rating_col = find_col(['Предыдущий рейтинг', 'Отличие рейтинг']) or 'Предыдущий рейтинг'

    st.write("**Найденные колонки:**")
    st.write(f"Площадка: {platform_col}")
    st.write(f"Статус: {status_col}")
    st.write(f"Наименование: {name_col}")
    st.write(f"Рейтинг: {rating_col}")
    st.write(f"Кол-во отзывов: {reviews_col}")

    # Фильтры
    platforms = ['Лемана про', 'Лемана про МП', 'Мегастрой', 'Максидом', 'Петрович', 'Все инструменты']
    df = df[df[platform_col].isin(platforms)]
    df = df[~df[status_col].astype(str).str.contains('Закрыт', na=False)]

    # Приводим числа
    for col in [rating_col, reviews_col, prev_rating_col]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    def get_priority(row):
        rating = row.get(rating_col, 0)
        prev = row.get(prev_rating_col, rating)
        reviews = row.get(reviews_col, 0)
        name = str(row.get(name_col, '')).lower()

        if rating <= 3.9:
            return 1, "1. Критично низкий рейтинг"
        if rating >= 4.0 and prev > rating:
            return 2, "2. Спад рейтинга"
        if rating <= 4.5 and reviews <= 5:
            return 3, "3. Рейтинг ≤4.5 + мало отзывов"
        if any(x in name for x in ['прожектор','удлинитель','садов','светильник','фонарь']) and (rating < 4.5 or reviews <= 5):
            return 4, "4. Сезонный товар"
        return 5, "5. Стандарт"

    df[['Приоритет', 'Причина']] = df.apply(get_priority, axis=1, result_type='expand')

    df = df.sort_values(by=['Приоритет', 'Рейтинг'])

    st.dataframe(df, use_container_width=True)

    if st.button("💾 Экспорт в Excel"):
        filename = f"Приоритет_отзывов_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
        df.to_excel(filename, index=False)
        st.success("Файл готов!")
        st.download_button("Скачать", data=open(filename, "rb").read(), file_name=filename)
