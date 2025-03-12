import streamlit as st
import pandas as pd
import os
import json
import datetime
import numpy as np

# ページ設定
st.set_page_config(
    page_title="12条点検 Web アプリ",
    layout="wide",
    initial_sidebar_state="expanded"
)

# タイトル
st.title("12条点検 Web アプリ")

# マスターデータの読み込み
def load_master_data(file_path, encoding='utf-8'):
    try:
        if os.path.exists(file_path):
            df = pd.read_csv(file_path, encoding=encoding)
            return df.iloc[:, 0].tolist()
        else:
            st.warning(f"マスターデータファイル {file_path} が見つかりません。")
            return []
    except Exception as e:
        st.error(f"マスターデータの読み込みエラー: {e}")
        return []

# マスターデータの読み込み
location_master = load_master_data("master/location_master.csv")
deterioration_master = load_master_data("master/deterioration_master.csv")

# セッション状態の初期化
if 'deterioration_items' not in st.session_state:
    st.session_state.deterioration_items = []
if 'next_deterioration_id' not in st.session_state:
    st.session_state.next_deterioration_id = 1

# タブの作成
tab1, tab2 = st.tabs(["点検入力", "データ閲覧"])

# 点検入力タブ
with tab1:
    st.header("点検情報入力")
    
    # 基本情報セクション
    col1, col2 = st.columns(2)
    with col1:
        inspection_date = st.date_input("点検日", value=datetime.date.today())
        inspector_name = st.text_input("点検者名")
    
    with col2:
        site_name = st.text_input("現場名")
        building_name = st.text_input("棟名")
        remarks = st.text_area("備考", height=100)
    
    st.divider()
    
    # 劣化内容セクション
    st.subheader("劣化内容入力")
    
    # 劣化内容入力フォーム
    with st.form(key="deterioration_form"):
        st.write(f"劣化番号: {st.session_state.next_deterioration_id}")
        
        # 場所の入力（直接入力も可能）
        location = st.text_input(
            "場所",
            key="location_input"
        )
        
        # 場所の候補リスト
        location_selection = st.selectbox(
            "場所の候補から選択",
            options=[""] + location_master,
            key="location_selection",
            label_visibility="collapsed"
        )
        
        # 場所の候補が選択された場合、入力欄に反映
        if location_selection and location_selection != st.session_state.get("prev_location_selection", ""):
            st.session_state["prev_location_selection"] = location_selection
            st.session_state["location_input"] = location_selection
            st.rerun()
        
        # 劣化名の入力（直接入力も可能）
        deterioration_name = st.text_input(
            "劣化名",
            key="deterioration_name_input"
        )
        
        # 劣化名の候補リスト
        deterioration_selection = st.selectbox(
            "劣化名の候補から選択",
            options=[""] + deterioration_master,
            key="deterioration_selection",
            label_visibility="collapsed"
        )
        
        # 劣化名の候補が選択された場合、入力欄に反映
        if deterioration_selection and deterioration_selection != st.session_state.get("prev_deterioration_selection", ""):
            st.session_state["prev_deterioration_selection"] = deterioration_selection
            st.session_state["deterioration_name_input"] = deterioration_selection
            st.rerun()
        
        # 写真番号の入力
        photo_number = st.text_input("写真番号")
        
        # 追加ボタン
        submit_button = st.form_submit_button("追加")
        
        if submit_button:
            if location and deterioration_name:  # 場所と劣化名は必須
                # 劣化項目の追加
                deterioration_item = {
                    "id": st.session_state.next_deterioration_id,
                    "location": location,
                    "deterioration_name": deterioration_name,
                    "photo_number": photo_number
                }
                
                st.session_state.deterioration_items.append(deterioration_item)
                st.session_state.next_deterioration_id += 1
                
                st.success("劣化項目を追加しました。")
                st.rerun()
            else:
                st.error("場所と劣化名は必須項目です。")
    
    # 劣化項目の一覧表示
    if st.session_state.deterioration_items:
        st.subheader("入力済み劣化項目")
        
        # DataFrameに変換して表示
        df_items = pd.DataFrame(st.session_state.deterioration_items)
        st.dataframe(df_items, use_container_width=True)
        
        # 削除機能
        if st.button("選択した項目を削除"):
            st.session_state.deterioration_items = []
            st.success("すべての項目を削除しました。")
            st.rerun()
    
    # 保存ボタン
    if st.session_state.deterioration_items:
        if st.button("点検データを保存"):
            try:
                # 保存先ディレクトリの確認
                os.makedirs("data", exist_ok=True)
                
                # 基本情報と劣化項目を結合
                inspection_data = []
                
                for item in st.session_state.deterioration_items:
                    row = {
                        "点検日": inspection_date.strftime("%Y-%m-%d"),
                        "点検者名": inspector_name,
                        "現場名": site_name,
                        "棟名": building_name,
                        "備考": remarks,
                        "劣化番号": item["id"],
                        "場所": item["location"],
                        "劣化名": item["deterioration_name"],
                        "写真番号": item["photo_number"]
                    }
                    inspection_data.append(row)
                
                # DataFrameに変換
                df_save = pd.DataFrame(inspection_data)
                
                # CSVファイルに保存
                file_path = "data/inspection_data.csv"
                
                # 既存ファイルがある場合は追記
                if os.path.exists(file_path):
                    df_existing = pd.read_csv(file_path, encoding="utf-8-sig")
                    df_combined = pd.concat([df_existing, df_save], ignore_index=True)
                    df_combined.to_csv(file_path, index=False, encoding="utf-8-sig")
                else:
                    df_save.to_csv(file_path, index=False, encoding="utf-8-sig")
                
                st.success("点検データを保存しました。")
                
                # セッション状態のリセット
                st.session_state.deterioration_items = []
                st.session_state.next_deterioration_id = 1
                
                st.rerun()
            
            except Exception as e:
                st.error(f"保存中にエラーが発生しました: {e}")

# データ閲覧タブ
with tab2:
    st.header("点検データ閲覧")
    
    # データファイルの読み込み
    file_path = "data/inspection_data.csv"
    
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path, encoding="utf-8-sig")
            
            # 検索・フィルタリング機能
            st.subheader("データ検索")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                search_date = st.date_input("点検日で検索", value=None, key="search_date")
            
            with col2:
                search_site = st.text_input("現場名で検索", key="search_site")
            
            with col3:
                search_photo = st.text_input("写真番号で検索", key="search_photo")
            
            # フィルタリング処理
            filtered_df = df.copy()
            
            if search_date:
                search_date_str = search_date.strftime("%Y-%m-%d")
                filtered_df = filtered_df[filtered_df["点検日"] == search_date_str]
            
            if search_site:
                filtered_df = filtered_df[filtered_df["現場名"].str.contains(search_site, na=False)]
            
            if search_photo:
                filtered_df = filtered_df[filtered_df["写真番号"].astype(str).str.contains(search_photo, na=False)]
            
            # データ表示
            st.subheader("点検データ")
            st.dataframe(filtered_df, use_container_width=True)
            
            # CSVダウンロード機能
            csv = filtered_df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
            st.download_button(
                label="CSVダウンロード",
                data=csv,
                file_name="inspection_data_export.csv",
                mime="text/csv",
            )
        
        except Exception as e:
            st.error(f"データ読み込み中にエラーが発生しました: {e}")
    
    else:
        st.info("保存された点検データがありません。点検入力タブからデータを入力してください。") 