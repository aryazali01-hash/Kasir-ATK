import streamlit as st
import pandas as pd
from datetime import datetime

# Konfigurasi Halaman
st.set_page_config(page_title="Kasir & Stok Toko ATK", page_icon="📚", layout="wide")

# Inisialisasi Database Produk di Session State
if 'products' not in st.session_state:
    st.session_state.products = pd.DataFrame([
        {"ID": 1, "Nama Barang": "Kertas HVS A4 (Rim)", "Kategori": "Kertas", "Modal": 48000, "Jual": 55000, "Stok": 15},
        {"ID": 2, "Nama Barang": "Pulpen Standard AE7 (Pcs)", "Kategori": "Alat Tulis", "Modal": 2200, "Jual": 3000, "Stok": 100},
        {"ID": 3, "Nama Barang": "Buku Tulis Sidu 38 Lembar", "Kategori": "Buku", "Modal": 3200, "Jual": 4000, "Stok": 60},
        {"ID": 4, "Nama Barang": "Lakban Bening Besar", "Kategori": "Aksesoris", "Modal": 9000, "Jual": 12000, "Stok": 25},
        {"ID": 5, "Nama Barang": "Jilid Dokumen (Jasa)", "Kategori": "Jasa", "Modal": 1000, "Jual": 5000, "Stok": 999}
    ])

# Inisialisasi Riwayat Transaksi
if 'transactions' not in st.session_state:
    st.session_state.transactions = []

# Inisialisasi Status Login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None

# ================= SISTEM LOGIN =================
if not st.session_state.logged_in:
    st.title("🔐 Login Sistem Toko ATK")
    role_choice = st.selectbox("Masuk Sebagai:", ["Kasir", "Owner / Pemilik"])
    
    if role_choice == "Owner / Pemilik":
        password = st.text_input("Password Owner:", type="password")
        if st.button("Login"):
            if password == "admin123": # Password default owner
                st.session_state.logged_in = True
                st.session_state.role = "Owner"
                st.rerun()
            else:
                st.error("Password salah! (Coba: admin123)")
    else:
        if st.button("Masuk sebagai Kasir"):
            st.session_state.logged_in = True
            st.session_state.role = "Kasir"
            st.rerun()
    st.stop()

# ================= PANEL ATAS & LOGOUT =================
st.sidebar.title(f"👤 Peran: {st.session_state.role}")
if st.sidebar.button("Keluar / Logout"):
    st.session_state.logged_in = False
    st.session_state.role = None
    st.rerun()

st.title("📚 Kasir & Manajemen Stok Toko ATK")
st.markdown("---")

# ================= PENGATURAN HAK AKSES MENU =================
if st.session_state.role == "Kasir":
    # Kasir hanya melihat Tab Kasir saja
    tabs = ["🛒 Kasir (POS)"]
else:
    # Owner melihat semua menu
    tabs = ["🛒 Kasir (POS)", "📦 Stok & Impor Data", "📊 Laporan Keuangan & Laba"]

if len(tabs) == 1:
    tab1 = st.container()
else:
    tab_obj = st.tabs(tabs)
    tab1 = tab_obj[0]

# ================= TAB 1: KASIR (POS) =================
with tab1 if len(tabs) == 1 else tab_obj[0]:
    st.subheader("Kasir Penjualan Harian")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        df_prod = st.session_state.products
        selected_name = st.selectbox("Cari / Pilih Barang:", df_prod["Nama Barang"].tolist(), key="pos_select")
        
        prod_row = df_prod[df_prod["Nama Barang"] == selected_name].iloc[0]
        max_stock = int(prod_row["Stok"])
        unit_price = float(prod_row["Jual"])
        
        st.info(f"Harga Satuan: **Rp {unit_price:,.0f}** | Stok Tersedia: **{max_stock}**")
        
        qty = st.number_input("Jumlah Beli:", min_value=1, max_value=max(1, max_stock), value=1, step=1)
        
        if st.button("➕ Tambah ke Keranjang", type="primary"):
            if 'cart' not in st.session_state:
                st.session_state.cart = []
            
            found = False
            for item in st.session_state.cart:
                if item["Nama Barang"] == selected_name:
                    item["Qty"] += qty
                    item["Subtotal"] = item["Qty"] * item["Harga Jual"]
                    found = True
                    break
            
            if not found:
                st.session_state.cart.append({
                    "Nama Barang": selected_name,
                    "Harga Jual": unit_price,
                    "Modal": float(prod_row["Modal"]),
                    "Qty": qty,
                    "Subtotal": unit_price * qty
                })
            st.success(f"{qty}x {selected_name} ditambahkan!")

    with col2:
        st.subheader("Keranjang Belanja")
        if 'cart' in st.session_state and len(st.session_state.cart) > 0:
            cart_df = pd.DataFrame(st.session_state.cart)
            st.dataframe(cart_df[["Nama Barang", "Qty", "Subtotal"]], hide_index=True)
            
            total_belanja = cart_df["Subtotal"].sum()
            st.markdown(f"### Total: Rp {total_belanja:,.0f}")
            
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("❌ Kosongkan"):
                    st.session_state.cart = []
                    st.rerun()
            with col_b2:
                if st.button("✅ Selesaikan Bayar"):
                    for item in st.session_state.cart:
                        idx = st.session_state.products[st.session_state.products["Nama Barang"] == item["Nama Barang"]].index[0]
                        st.session_state.products.at[idx, "Stok"] -= item["Qty"]
                        
                        st.session_state.transactions.append({
                            "Waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "Nama Barang": item["Nama Barang"],
                            "Qty": item["Qty"],
                            "Omzet": item["Subtotal"],
                            "Modal": item["Modal"] * item["Qty"],
                            "Laba": item["Subtotal"] - (item["Modal"] * item["Qty"])
                        })
                    
                    st.success("Transaksi Berhasil Disimpan & Stok Terpotong!")
                    st.session_state.cart = []
                    st.rerun()
        else:
            st.write("Keranjang masih kosong.")

# ================= MENU KHUSUS OWNER (MANAJEMEN & LAPORAN) =================
if len(tabs) > 1:
    # TAB 2: STOK & IMPOR FILE
    with tab_obj[1]:
        st.subheader("Manajemen Stok & Impor File Massal")
        st.write("Ubah stok/harga langsung di tabel, atau unggah file CSV berisi daftar produk baru.")
        
        # Fitur Impor File CSV
        with st.expander("📁 Impor Data Produk dari File CSV"):
            st.write("Format kolom pada file CSV wajib memiliki: `Nama Barang`, `Kategori`, `Modal`, `Jual`, `Stok`")
            uploaded_file = st.file_uploader("Pilih file CSV", type=["csv"])
            if uploaded_file is not None:
                try:
                    imported_df = pd.read_csv(uploaded_file)
                    required_cols = ["Nama Barang", "Kategori", "Modal", "Jual", "Stok"]
                    if all(col in imported_df.columns for col in required_cols):
                        if "ID" not in imported_df.columns:
                            imported_df["ID"] = range(int(datetime.now().timestamp()), int(datetime.now().timestamp()) + len(imported_df))
                        st.session_state.products = imported_df[["ID", "Nama Barang", "Kategori", "Modal", "Jual", "Stok"]]
                        st.success("Data produk berhasil diimpor secara massal!")
                        st.rerun()
                    else:
                        st.error(f"Format kolom kurang tepat. Wajib ada: {required_cols}")
                except Exception as e:
                    st.error(f"Terjadi kesalahan saat membaca file: {e}")

        edited_df = st.data_editor(st.session_state.products, num_rows="dynamic", key="stock_editor")
        st.session_state.products = edited_df
        
        st.markdown("---")
        st.subheader("Tambah Barang Baru Secara Manual")
        with st.form("add_product_form"):
            c1, c2, c3, c4, c5 = st.columns(5)
            with c1: new_id = int(datetime.now().timestamp())
            with c2: new_name = st.text_input("Nama Barang")
            with c3: new_cat = st.text_input("Kategori", value="Umum")
            with c4: new_modal = st.number_input("Harga Modal (Rp)", min_value=0, value=1000)
            with c5: new_jual = st.number_input("Harga Jual (Rp)", min_value=0, value=1500)
            new_stok = st.number_input("Stok Awal", min_value=0, value=10)
            
            submitted = st.form_submit_button("Simpan Barang Baru")
            if submitted and new_name:
                new_row = pd.DataFrame([{
                    "ID": new_id, "Nama Barang": new_name, "Kategori": new_cat, 
                    "Modal": new_modal, "Jual": new_jual, "Stok": new_stok
                }])
                st.session_state.products = pd.concat([st.session_state.products, new_row], ignore_index=True)
                st.success(f"Barang '{new_name}' berhasil ditambahkan!")
                st.rerun()

    # TAB 3: LAPORAN KEUANGAN
    with tab_obj[2]:
        st.subheader("Laporan Penjualan & Laba Bersih")
        
        if len(st.session_state.transactions) > 0:
            trx_df = pd.DataFrame(st.session_state.transactions)
            
            total_omzet = trx_df["Omzet"].sum()
            total_modal = trx_df["Modal"].sum()
            total_laba = trx_df["Laba"].sum()
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Omzet Penjualan", f"Rp {total_omzet:,.0f}")
            m2.metric("Total Harga Modal (HPP)", f"Rp {total_modal:,.0f}")
            m3.metric("Total Laba Bersih", f"Rp {total_laba:,.0f}", delta="Keuntungan")
            
            st.markdown("---")
            st.subheader("Riwayat Detail Transaksi")
            st.dataframe(trx_df, hide_index=True)
        else:
            st.info("Belum ada transaksi yang tercatat hari ini.")
