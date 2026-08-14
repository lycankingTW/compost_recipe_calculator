import math

import pandas as pd
import streamlit as st


# =========================================================
# 1. 頁面設定
# =========================================================
st.set_page_config(
    page_title="堆肥配方計算機",
    page_icon="🌱",
    layout="centered",
)


# =========================================================
# 2. CSS：簡化 Streamlit 介面與頁面美化
#
# 注意：隱藏選單僅降低使用者直接點擊 GitHub 連結的便利性，
# 不能取代私人儲存庫或其他原始碼存取控制。
# =========================================================
st.markdown(
    """
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}

        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stHeader"] {
            display: none;
        }

        [data-testid="stStatusWidget"],
        #GithubIcon {
            visibility: hidden;
        }

        .stApp {
            background:
                radial-gradient(circle at 8% 5%, rgba(197, 225, 165, 0.45), transparent 28rem),
                #f4f7ef;
        }

        [data-testid="stAppViewContainer"] > .main {
            background: transparent;
        }

        .block-container {
            max-width: 980px;
            padding-top: 2.4rem;
            padding-bottom: 4rem;
        }

        h1, h2, h3 {
            color: #1f5d35;
            letter-spacing: 0.01em;
        }

        div[data-testid="stMetric"] {
            background-color: #ffffff;
            border: 1px solid #c7d9bc;
            border-left: 6px solid #2e7d32;
            border-radius: 0.75rem;
            padding: 1rem;
            box-shadow: 0 8px 22px rgba(31, 93, 53, 0.07);
        }

        div[data-testid="stExpander"] {
            background-color: rgba(255, 255, 255, 0.88);
            border: 1px solid #c7d9bc;
            border-radius: 0.75rem;
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            background-color: rgba(255, 255, 255, 0.82);
            border-radius: 0.8rem;
        }

        .scientific-note {
            border-left: 5px solid #d98c2b;
            background: #fff9ec;
            color: #59451f;
            border-radius: 0.4rem;
            padding: 0.85rem 1rem;
            margin: 0.6rem 0 1rem 0;
        }

        .copyright {
            color: #617064;
            font-size: 0.82rem;
            text-align: center;
            margin-top: 1.5rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 3. 內建資材資料庫
#
# c_pct、n_pct：乾物基準百分比（% DM）
# moisture_pct：濕基含水率（% wet basis）
#
# 公開使用前，請逐筆核對正式資料來源及分析基準。
# =========================================================
MATERIALS = {
    "chicken_manure": {
        "group": "禽畜糞類",
        "name": "雞糞",
        "c_pct": 34.0,
        "n_pct": 4.2,
        "moisture_pct": 56.0,
    },
    "pig_manure": {
        "group": "禽畜糞類",
        "name": "豬糞",
        "c_pct": 43.0,
        "n_pct": 3.0,
        "moisture_pct": 72.0,
    },
    "cattle_manure": {
        "group": "禽畜糞類",
        "name": "牛糞",
        "c_pct": 51.0,
        "n_pct": 2.7,
        "moisture_pct": 84.0,
    },
    "rice_straw": {
        "group": "農業副產物",
        "name": "稻草",
        "c_pct": 53.0,
        "n_pct": 0.8,
        "moisture_pct": 14.0,
    },
    "rice_husk": {
        "group": "農業副產物",
        "name": "稻殼",
        "c_pct": 52.0,
        "n_pct": 0.5,
        "moisture_pct": 12.0,
    },
    "rice_bran": {
        "group": "農業副產物",
        "name": "米糠",
        "c_pct": 50.0,
        "n_pct": 2.1,
        "moisture_pct": 15.0,
    },
    "peanut_shell": {
        "group": "農業副產物",
        "name": "花生殼",
        "c_pct": 53.0,
        "n_pct": 1.6,
        "moisture_pct": 15.0,
    },
    "fresh_sawdust": {
        "group": "木雜草類",
        "name": "新鮮木屑",
        "c_pct": 48.0,
        "n_pct": 0.1,
        "moisture_pct": 10.0,
    },
    "spent_mushroom_sawdust": {
        "group": "木雜草類",
        "name": "廢棄菇類木屑",
        "c_pct": 45.0,
        "n_pct": 0.7,
        "moisture_pct": 67.0,
    },
    "shiitake_bag_sawdust": {
        "group": "木雜草類",
        "name": "香菇太空包木屑",
        "c_pct": 44.6,
        "n_pct": 1.25,
        "moisture_pct": 60.0,
    },
    "broadleaf_litter": {
        "group": "木雜草類",
        "name": "闊葉樹落葉",
        "c_pct": 55.0,
        "n_pct": 1.2,
        "moisture_pct": 15.0,
    },
    "soybean_meal": {
        "group": "食品副產物",
        "name": "豆粕",
        "c_pct": 48.0,
        "n_pct": 7.5,
        "moisture_pct": 10.0,
    },
    "rapeseed_meal": {
        "group": "食品副產物",
        "name": "菜籽粕",
        "c_pct": 48.0,
        "n_pct": 6.0,
        "moisture_pct": 10.0,
    },
    "brewers_grain": {
        "group": "食品副產物",
        "name": "啤酒糟",
        "c_pct": 49.0,
        "n_pct": 4.82,
        "moisture_pct": 75.0,
    },
    "sesbania_fresh": {
        "group": "綠肥作物",
        "name": "田菁（生鮮）",
        "c_pct": 47.0,
        "n_pct": 2.65,
        "moisture_pct": 80.0,
    },
    "sunn_hemp_fresh": {
        "group": "綠肥作物",
        "name": "太陽麻（生鮮）",
        "c_pct": 54.0,
        "n_pct": 1.78,
        "moisture_pct": 80.0,
    },
    "custom": {
        "group": "其他",
        "name": "自訂材料",
        "c_pct": None,
        "n_pct": None,
        "moisture_pct": None,
    },
}

MATERIAL_IDS = list(MATERIALS.keys())
MATERIAL_LABELS = {
    material_id: f"{item['group']}｜{item['name']}"
    for material_id, item in MATERIALS.items()
}


# =========================================================
# 4. Session State 與材料列管理
# =========================================================
def new_material_row(row_id, material_id="rice_straw"):
    return {
        "row_id": row_id,
        "material_id": material_id,
        "wet_weight": 0.0,
        "custom_name": "",
        "custom_c_pct": 0.0,
        "custom_n_pct": 0.0,
        "custom_moisture_pct": 0.0,
    }


def initialize_state():
    if "material_rows" not in st.session_state:
        st.session_state.material_rows = [
            new_material_row(0, "chicken_manure"),
            new_material_row(1, "rice_straw"),
        ]

    if "next_row_id" not in st.session_state:
        st.session_state.next_row_id = 2


def add_material_row():
    row_id = st.session_state.next_row_id
    st.session_state.material_rows.append(
        new_material_row(row_id, "rice_straw")
    )
    st.session_state.next_row_id += 1


def remove_material_row(row_id):
    if len(st.session_state.material_rows) <= 1:
        return

    st.session_state.material_rows = [
        row
        for row in st.session_state.material_rows
        if row["row_id"] != row_id
    ]


def reset_calculator():
    # 清除材料元件的舊鍵值，避免重設後被既有 widget state 覆寫。
    keys_to_delete = [
        key
        for key in st.session_state.keys()
        if key.startswith(
            (
                "material_select_",
                "wet_weight_",
                "custom_name_",
                "custom_c_",
                "custom_n_",
                "custom_m_",
            )
        )
    ]
    for key in keys_to_delete:
        del st.session_state[key]

    st.session_state.material_rows = [
        new_material_row(0, "chicken_manure"),
        new_material_row(1, "rice_straw"),
    ]
    st.session_state.next_row_id = 2


initialize_state()


# =========================================================
# 5. 計算函式
# =========================================================
def calculate_compost(rows):
    """
    計算混合配方之總濕重、水分、乾物、碳、氮、C/N 與含水率。

    計算基準：
    - 投入重量：濕重（kg as-is）
    - 含水率：濕基（% wet basis）
    - 碳與氮：乾物基準（% DM）
    """
    detail_records = []
    errors = []

    total_wet_weight = 0.0
    total_water_mass = 0.0
    total_dry_mass = 0.0
    total_carbon_mass = 0.0
    total_nitrogen_mass = 0.0

    for position, row in enumerate(rows, start=1):
        material_id = row["material_id"]
        wet_weight = float(row["wet_weight"])

        if material_id == "custom":
            material_name = row["custom_name"].strip() or f"自訂材料 {position}"
            c_pct = float(row["custom_c_pct"])
            n_pct = float(row["custom_n_pct"])
            moisture_pct = float(row["custom_moisture_pct"])
        else:
            material = MATERIALS[material_id]
            material_name = material["name"]
            c_pct = float(material["c_pct"])
            n_pct = float(material["n_pct"])
            moisture_pct = float(material["moisture_pct"])

        values = (wet_weight, c_pct, n_pct, moisture_pct)
        if not all(math.isfinite(value) for value in values):
            errors.append(f"第 {position} 項材料含有非有限數值。")
            continue

        if wet_weight < 0:
            errors.append(f"第 {position} 項材料的濕重不可小於 0。")
            continue
        if not 0 <= c_pct <= 100:
            errors.append(f"第 {position} 項材料的碳含量應介於 0–100%。")
            continue
        if not 0 <= n_pct <= 100:
            errors.append(f"第 {position} 項材料的氮含量應介於 0–100%。")
            continue
        if not 0 <= moisture_pct <= 100:
            errors.append(f"第 {position} 項材料的含水率應介於 0–100%。")
            continue

        # 0 kg 的材料不納入質量平衡。
        if wet_weight == 0:
            continue

        water_mass = wet_weight * moisture_pct / 100
        dry_mass = wet_weight * (1 - moisture_pct / 100)
        carbon_mass = dry_mass * c_pct / 100
        nitrogen_mass = dry_mass * n_pct / 100

        total_wet_weight += wet_weight
        total_water_mass += water_mass
        total_dry_mass += dry_mass
        total_carbon_mass += carbon_mass
        total_nitrogen_mass += nitrogen_mass

        detail_records.append(
            {
                "材料序號": position,
                "材料": material_name,
                "濕重（kg）": wet_weight,
                "含水率（%）": moisture_pct,
                "水分質量（kg）": water_mass,
                "乾物重（kg）": dry_mass,
                "碳含量（% DM）": c_pct,
                "氮含量（% DM）": n_pct,
                "碳質量（kg）": carbon_mass,
                "氮質量（kg）": nitrogen_mass,
            }
        )

    moisture = (
        total_water_mass / total_wet_weight * 100
        if total_wet_weight > 0
        else None
    )
    cn_ratio = (
        total_carbon_mass / total_nitrogen_mass
        if total_nitrogen_mass > 0
        else None
    )

    return {
        "errors": errors,
        "details": pd.DataFrame(detail_records),
        "total_wet_weight": total_wet_weight,
        "total_water_mass": total_water_mass,
        "total_dry_mass": total_dry_mass,
        "total_carbon_mass": total_carbon_mass,
        "total_nitrogen_mass": total_nitrogen_mass,
        "moisture": moisture,
        "cn_ratio": cn_ratio,
    }


# =========================================================
# 6. 詳細公式與代入過程
# =========================================================
def show_detailed_calculation(result):
    details = result["details"]

    with st.expander("查看詳細計算公式與代入過程", expanded=False):
        st.markdown("### 1. 符號與分析基準")

        st.latex(r"W_i=\text{第 }i\text{ 項材料的投入濕重（kg）}")
        st.latex(r"M_i=\text{第 }i\text{ 項材料的濕基含水率（小數）}")
        st.latex(r"C_i=\text{第 }i\text{ 項材料的乾物基準碳含量（小數）}")
        st.latex(r"N_i=\text{第 }i\text{ 項材料的乾物基準氮含量（小數）}")

        st.markdown(
            "百分比須除以 100 後代入，例如 56% 以 0.56 代入。"
        )

        st.markdown("### 2. 各材料計算公式")

        st.latex(r"W_{\mathrm{water},i}=W_iM_i")
        st.latex(
            r"W_{\mathrm{dry},i}"
            r"=W_i-W_{\mathrm{water},i}"
            r"=W_i(1-M_i)"
        )
        st.latex(r"W_{\mathrm{C},i}=W_{\mathrm{dry},i}C_i")
        st.latex(r"W_{\mathrm{N},i}=W_{\mathrm{dry},i}N_i")

        if details.empty:
            st.info("輸入材料重量後，系統將顯示逐項代入過程。")
            return

        st.markdown("### 3. 各材料實際代入")

        for _, record in details.iterrows():
            position = int(record["材料序號"])
            name = str(record["材料"])
            wet = float(record["濕重（kg）"])
            moisture_pct = float(record["含水率（%）"])
            water = float(record["水分質量（kg）"])
            dry = float(record["乾物重（kg）"])
            c_pct = float(record["碳含量（% DM）"])
            n_pct = float(record["氮含量（% DM）"])
            carbon = float(record["碳質量（kg）"])
            nitrogen = float(record["氮質量（kg）"])

            st.markdown(f"#### 材料 {position}：{name}")

            st.latex(
                rf"W_{{\mathrm{{water}},{position}}}"
                rf"={wet:.3f}\times\frac{{{moisture_pct:.2f}}}{{100}}"
                rf"={water:.3f}\ \mathrm{{kg}}"
            )
            st.latex(
                rf"W_{{\mathrm{{dry}},{position}}}"
                rf"={wet:.3f}\times"
                rf"\left(1-\frac{{{moisture_pct:.2f}}}{{100}}\right)"
                rf"={dry:.3f}\ \mathrm{{kg}}"
            )
            st.latex(
                rf"W_{{\mathrm{{C}},{position}}}"
                rf"={dry:.3f}\times\frac{{{c_pct:.2f}}}{{100}}"
                rf"={carbon:.3f}\ \mathrm{{kg}}"
            )
            st.latex(
                rf"W_{{\mathrm{{N}},{position}}}"
                rf"={dry:.3f}\times\frac{{{n_pct:.2f}}}{{100}}"
                rf"={nitrogen:.3f}\ \mathrm{{kg}}"
            )

        total_wet = float(result["total_wet_weight"])
        total_water = float(result["total_water_mass"])
        total_dry = float(result["total_dry_mass"])
        total_carbon = float(result["total_carbon_mass"])
        total_nitrogen = float(result["total_nitrogen_mass"])

        st.markdown("### 4. 混合配方總量")

        st.latex(
            rf"W_{{\mathrm{{wet,total}}}}"
            rf"=\sum_i W_i={total_wet:.3f}\ \mathrm{{kg}}"
        )
        st.latex(
            rf"W_{{\mathrm{{water,total}}}}"
            rf"=\sum_i W_{{\mathrm{{water}},i}}"
            rf"={total_water:.3f}\ \mathrm{{kg}}"
        )
        st.latex(
            rf"W_{{\mathrm{{dry,total}}}}"
            rf"=\sum_i W_{{\mathrm{{dry}},i}}"
            rf"={total_dry:.3f}\ \mathrm{{kg}}"
        )
        st.latex(
            rf"W_{{\mathrm{{C,total}}}}"
            rf"=\sum_i W_{{\mathrm{{C}},i}}"
            rf"={total_carbon:.3f}\ \mathrm{{kg}}"
        )
        st.latex(
            rf"W_{{\mathrm{{N,total}}}}"
            rf"=\sum_i W_{{\mathrm{{N}},i}}"
            rf"={total_nitrogen:.3f}\ \mathrm{{kg}}"
        )

        st.markdown("### 5. 綜合碳氮比")

        st.latex(
            r"\mathrm{C/N}_{\mathrm{mix}}"
            r"=\frac{\sum_i W_{\mathrm{C},i}}"
            r"{\sum_i W_{\mathrm{N},i}}"
        )

        if total_nitrogen > 0:
            cn_ratio = float(result["cn_ratio"])
            st.latex(
                rf"\mathrm{{C/N}}_{{\mathrm{{mix}}}}"
                rf"=\frac{{{total_carbon:.3f}}}{{{total_nitrogen:.3f}}}"
                rf"={cn_ratio:.2f}"
            )
        else:
            st.warning("總氮質量為 0 kg，分母為 0，因此 C/N 無法計算。")

        st.markdown("### 6. 整體含水率")

        st.latex(
            r"M_{\mathrm{mix}}"
            r"=\frac{\sum_i W_{\mathrm{water},i}}"
            r"{\sum_i W_i}\times100\%"
        )

        if total_wet > 0:
            moisture = float(result["moisture"])
            st.latex(
                rf"M_{{\mathrm{{mix}}}}"
                rf"=\frac{{{total_water:.3f}}}{{{total_wet:.3f}}}"
                rf"\times100\%={moisture:.2f}\%"
            )
        else:
            st.warning("總投入濕重為 0 kg，因此整體含水率無法計算。")

        st.markdown("### 7. 質量平衡檢核")

        balance_difference = total_wet - (total_water + total_dry)
        st.latex(
            r"W_{\mathrm{wet,total}}"
            r"=W_{\mathrm{water,total}}+W_{\mathrm{dry,total}}"
        )
        st.latex(
            rf"{total_wet:.3f}"
            rf"={total_water:.3f}+{total_dry:.3f}"
            rf"\quad"
            rf"\left(\Delta={balance_difference:.6f}\ \mathrm{{kg}}\right)"
        )

        st.caption(
            "畫面數值經四捨五入，個別顯示值相加可能產生極小差異；"
            "程式內部均以未四捨五入數值計算。"
        )


# =========================================================
# 7. 頁首與科學基準
# =========================================================
st.title("堆肥配方計算機")

st.caption(
    "依投入濕重、乾物基準碳氮含量及濕基含水率，"
    "估算混合資材的初始 C/N 與含水率。"
)

st.markdown(
    """
    <div class="scientific-note">
        <strong>計算基準：</strong>
        投入重量為實際濕重；碳、氮含量為乾物基準；含水率為濕基。
        內建數值屬代表性參考值，正式配方應優先採用該批材料實測值。
    </div>
    """,
    unsafe_allow_html=True,
)

with st.expander("使用限制與科學判讀", expanded=False):
    st.markdown(
        """
        - C/N 為總碳質量除以總氮質量，不是各材料 C/N 的算術平均。
        - 建議區間僅供好氧堆肥初始配方估算。
        - 實際發酵仍受粒徑、孔隙度、自由空氣空間、通氣、溫度、
          pH、氧氣濃度與原料生物可分解性影響。
        - 禽畜糞及農業副產物的成分會隨批次、季節、墊料與儲存條件改變。
        """
    )


# =========================================================
# 8. 動態材料輸入介面
# =========================================================
st.subheader("一、輸入材料")

for display_index, row in enumerate(
    list(st.session_state.material_rows),
    start=1,
):
    row_id = row["row_id"]

    with st.container(border=True):
        title_col, remove_col = st.columns([5, 1])

        with title_col:
            st.markdown(f"#### 材料 {display_index}")

        with remove_col:
            st.button(
                "移除",
                key=f"remove_{row_id}",
                on_click=remove_material_row,
                args=(row_id,),
                disabled=len(st.session_state.material_rows) <= 1,
                use_container_width=True,
            )

        selected_index = MATERIAL_IDS.index(row["material_id"])

        material_id = st.selectbox(
            "材料種類",
            options=MATERIAL_IDS,
            index=selected_index,
            format_func=lambda item_id: MATERIAL_LABELS[item_id],
            key=f"material_select_{row_id}",
        )
        row["material_id"] = material_id

        row["wet_weight"] = st.number_input(
            "實際濕重（kg）",
            min_value=0.0,
            max_value=1_000_000.0,
            value=float(row["wet_weight"]),
            step=1.0,
            format="%.2f",
            key=f"wet_weight_{row_id}",
            help="請輸入材料在目前含水狀態下的實際重量。",
        )

        if material_id == "custom":
            row["custom_name"] = st.text_input(
                "自訂材料名稱",
                value=row["custom_name"],
                key=f"custom_name_{row_id}",
                placeholder="例如：藍莓修剪枝條",
            )

            c_col, n_col, m_col = st.columns(3)

            with c_col:
                row["custom_c_pct"] = st.number_input(
                    "碳含量（% DM）",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(row["custom_c_pct"]),
                    step=0.1,
                    format="%.2f",
                    key=f"custom_c_{row_id}",
                )

            with n_col:
                row["custom_n_pct"] = st.number_input(
                    "氮含量（% DM）",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(row["custom_n_pct"]),
                    step=0.1,
                    format="%.2f",
                    key=f"custom_n_{row_id}",
                )

            with m_col:
                row["custom_moisture_pct"] = st.number_input(
                    "含水率（%，濕基）",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(row["custom_moisture_pct"]),
                    step=0.1,
                    format="%.2f",
                    key=f"custom_m_{row_id}",
                )
        else:
            material = MATERIALS[material_id]
            st.info(
                f"內建值：C = {material['c_pct']:.2f}% DM；"
                f"N = {material['n_pct']:.2f}% DM；"
                f"含水率 = {material['moisture_pct']:.2f}%（濕基）"
            )

button_col1, button_col2 = st.columns(2)

with button_col1:
    st.button(
        "＋ 新增另一種材料",
        on_click=add_material_row,
        use_container_width=True,
        type="primary",
    )

with button_col2:
    st.button(
        "重設",
        on_click=reset_calculator,
        use_container_width=True,
    )


# =========================================================
# 9. 結果、判讀及資料下載
# =========================================================
result = calculate_compost(st.session_state.material_rows)

st.subheader("二、估算結果")

if result["errors"]:
    for error in result["errors"]:
        st.error(error)

if result["total_wet_weight"] <= 0:
    st.warning("請至少為一項材料輸入大於 0 kg 的實際濕重。")
else:
    cn_ratio = result["cn_ratio"]
    moisture = result["moisture"]

    metric_col1, metric_col2, metric_col3 = st.columns(3)

    with metric_col1:
        st.metric(
            "綜合碳氮比（C/N）",
            "無法計算" if cn_ratio is None else f"{cn_ratio:.1f}",
        )

    with metric_col2:
        st.metric(
            "整體含水率",
            "無法計算" if moisture is None else f"{moisture:.1f}%",
        )

    with metric_col3:
        st.metric(
            "總投入濕重",
            f"{result['total_wet_weight']:.1f} kg",
        )

    st.markdown("#### 配方判讀")

    if cn_ratio is None:
        st.warning("C/N 無法計算：目前配方的總氮質量為 0。")
    elif 25 <= cn_ratio <= 35:
        st.success("C/N 位於一般好氧堆肥的建議初始區間（25–35）。")
    elif cn_ratio < 25:
        st.warning(
            "C/N 偏低。可評估增加稻草、稻殼或木屑等高碳材料；"
            "實際調整仍須考慮材料可分解性與通氣性。"
        )
    else:
        st.warning(
            "C/N 偏高。可評估增加禽畜糞或豆粕等相對高氮材料；"
            "實際調整仍須考慮氨揮失與臭味風險。"
        )

    if moisture is None:
        st.warning("目前無法計算混合含水率。")
    elif 50 <= moisture <= 65:
        st.success("含水率位於一般好氧堆肥的建議初始區間（50–65%）。")
    elif moisture < 50:
        st.warning("混合物偏乾，可評估加水或增加高含水材料。")
    else:
        st.warning(
            "混合物偏濕，可評估加入乾燥木屑或稻殼，"
            "並同步確認堆體孔隙度與通氣性。"
        )

    st.markdown("#### 質量平衡摘要")

    summary_df = pd.DataFrame(
        {
            "指標": [
                "總濕重",
                "總水分質量",
                "總乾物重",
                "總碳質量",
                "總氮質量",
            ],
            "數值（kg）": [
                result["total_wet_weight"],
                result["total_water_mass"],
                result["total_dry_mass"],
                result["total_carbon_mass"],
                result["total_nitrogen_mass"],
            ],
        }
    )

    st.dataframe(
        summary_df.style.format({"數值（kg）": "{:.3f}"}),
        use_container_width=True,
        hide_index=True,
    )

    if not result["details"].empty:
        st.markdown("#### 各材料計算明細")

        st.dataframe(
            result["details"].style.format(
                {
                    "濕重（kg）": "{:.3f}",
                    "含水率（%）": "{:.2f}",
                    "水分質量（kg）": "{:.3f}",
                    "乾物重（kg）": "{:.3f}",
                    "碳含量（% DM）": "{:.2f}",
                    "氮含量（% DM）": "{:.2f}",
                    "碳質量（kg）": "{:.3f}",
                    "氮質量（kg）": "{:.3f}",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

        csv_data = result["details"].to_csv(
            index=False,
            encoding="utf-8-sig",
        )

        st.download_button(
            label="下載配方計算明細（CSV）",
            data=csv_data,
            file_name="compost_formula_details.csv",
            mime="text/csv",
            use_container_width=True,
        )

# 即使尚未輸入重量，也先顯示一般公式。
show_detailed_calculation(result)


# =========================================================
# 10. 頁尾
# =========================================================
st.divider()

st.caption(
    "注意：本工具僅供堆肥初始配方估算。內建材料成分可能受來源、"
    "批次、季節、儲存與採樣方式影響；正式操作應優先採用實測資料，"
    "並配合溫度、氧氣、孔隙度、氣味及成熟度等指標判讀。"
)

st.markdown(
    """
    <div class="copyright">
        © 2026 林鈺荏。程式、資料整理及計算介面保留著作權；
        未經同意不得重製、散布或用於商業用途。
    </div>
    """,
    unsafe_allow_html=True,
)