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

    st.write("**Названия колонок в твоём файле:**")
    st.write(list(df.columns))

    # Безопасный фильтр
    status_col = [col for col in df.columns if 'татус' in col or 'Status' in col]
    status_col = status_col[0] if status_col else 'Статус'

    platform_col = [col for col in df.columns if 'лощадка' in col or 'Platform' in col]
    platform_col = platform_col[0] if platform_col else 'Площадка'

    # Фильтры
    platforms = ['Лемана про', 'Лемана про МП', 'Мегастрой', 'Максидом', 'Петрович', 'Все инструменты']
    df = df[df[platform_col].isin(platforms)]
    df = df[~df[status_col].astype(str).str.contains('Закрыт', na=False)]

    # Приводим числа
    for col in ['Рейтинг', 'Кол-во отзывов', 'Предыдущий рейтинг']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    def get_priority(row):
        rating = row.get('Рейтинг', 0)
        prev = row.get('Предыдущий рейтинг', rating)
        reviews = row.get('Кол-во отзывов', 0)
        name = str(row.get('Наименование', '')).lower()

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
