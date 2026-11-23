import streamlit as st
import requests
import pandas as pd

# 1. Configuración de página
st.set_page_config(page_title="Tech & Style Store", page_icon="🛍️", layout="wide")

# Estilos CSS personalizados para tarjetas de productos
st.markdown("""
    <style>
    .product-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    }
    .price-tag {
        font-size: 1.3rem;
        font-weight: bold;
        color: #16a34a;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Consumo de API Pública (con caché para rendimiento)
@st.cache_data(ttl=3600)
def obtener_productos():
    url = "https://fakestoreapi.com/products"
    try:
        respuesta = requests.get(url, timeout=10)
        respuesta.raise_for_status()
        return respuesta.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error al conectar con la API de productos: {e}")
        return []

# 3. Inicialización del Carrito de Compras en Session State
if 'carrito' not in st.session_state:
    st.session_state.carrito = {}

def agregar_al_carrito(producto):
    prod_id = str(producto['id'])
    if prod_id in st.session_state.carrito:
        st.session_state.carrito[prod_id]['cantidad'] += 1
    else:
        st.session_state.carrito[prod_id] = {
            'titulo': producto['title'],
            'precio': float(producto['price']),
            'imagen': producto['image'],
            'cantidad': 1
        }

def vaciar_carrito():
    st.session_state.carrito = {}

# Cargar datos desde la API
productos = obtener_productos()

# ==========================================
# BARRA LATERAL: FILTROS Y CARRITO
# ==========================================
st.sidebar.title("🛒 Carrito de Compras")

# Mostrar resumen del carrito en el sidebar
if not st.session_state.carrito:
    st.sidebar.info("Tu carrito está vacío. Agrega productos del catálogo.")
else:
    total_pagar = 0.0
    total_articulos = 0
    
    for prod_id, item in list(st.session_state.carrito.items()):
        subtotal = item['precio'] * item['cantidad']
        total_pagar += subtotal
        total_articulos += item['cantidad']
        
        with st.sidebar.container():
            st.markdown(f"**{item['titulo'][:30]}...**")
            c1, c2 = st.sidebar.columns([2, 1])
            c1.write(f"{item['cantidad']} x ${item['precio']:.2f} = **${subtotal:.2f}**")
            if c2.button("Eliminar", key=f"del_{prod_id}"):
                del st.session_state.carrito[prod_id]
                st.rerun()
            st.sidebar.divider()
            
    st.sidebar.subheader(f"Total ({total_articulos} arts.): ${total_pagar:,.2f} USD")
    
    col_btn1, col_btn2 = st.sidebar.columns(2)
    if col_btn1.button("🗑️ Vaciar", use_container_width=True):
        vaciar_carrito()
        st.rerun()
    if col_btn2.button("💳 Pagar", type="primary", use_container_width=True):
        st.session_state.checkout_activo = True

st.sidebar.divider()
st.sidebar.header("🔍 Filtros de Catálogo")

if productos:
    categorias = ["Todas"] + sorted(list(set(p['category'] for p in productos)))
    cat_sel = st.sidebar.selectbox("Categoría:", categorias)
    
    precios = [float(p['price']) for p in productos]
    max_precio = st.sidebar.slider("Precio máximo ($ USD):", min_value=0.0, max_value=max(precios), value=max(precios))
    busqueda = st.sidebar.text_input("Buscar producto:", placeholder="Ej. Jacket, SSD, Gold...")

# ==========================================
# CUERPO PRINCIPAL DE LA TIENDA
# ==========================================
st.title("🛍️ Tienda Online - Catálogo Dinámico (API)")
st.caption("Conectado en tiempo real a FakeStore API | Simulación de Comercio Electrónico")

# Simulación de pantalla de Checkout si presionó Pagar
if st.session_state.get('checkout_activo', False) and st.session_state.carrito:
    with st.container():
        st.success("✅ **Finalizar Compra (Simulación de Pasarela de Pago)**")
        with st.form("form_pago"):
            col_f1, col_f2 = st.columns(2)
            nombre = col_f1.text_input("Nombre Completo*", placeholder="Juan Pérez")
            correo = col_f2.text_input("Correo Electrónico*", placeholder="juan@ejemplo.com")
            direccion = st.text_input("Dirección de Envío*", placeholder="Av. Principal #123, Ciudad")
            metodo = st.selectbox("Método de Pago", ["Tarjeta de Crédito / Débito", "PayPal", "Transferencia Bancaria"])
            
            enviado = st.form_submit_button("Confirmar Pedido")
            if enviado:
                if nombre and correo and direccion:
                    st.balloons()
                    st.success(f"🎉 ¡Gracias por tu compra, {nombre}! Tu pedido ha sido procesado y enviado a {direccion}.")
                    vaciar_carrito()
                    st.session_state.checkout_activo = False
                else:
                    st.warning("Por favor completa todos los campos obligatorios.")
        if st.button("Cancelar y seguir comprando"):
            st.session_state.checkout_activo = False
            st.rerun()
    st.divider()

# Filtrar lista de productos
productos_filtrados = []
for p in productos:
    cumple_cat = (cat_sel == "Todas") or (p['category'] == cat_sel)
    cumple_precio = float(p['price']) <= max_precio
    cumple_texto = (not busqueda) or (busqueda.lower() in p['title'].lower()) or (busqueda.lower() in p['description'].lower())
    
    if cumple_cat and cumple_precio and cumple_texto:
        productos_filtrados.append(p)

st.write(f"Mostrando **{len(productos_filtrados)}** productos disponibles:")

# Mostrar cuadrícula de productos (3 columnas por fila)
cols = st.columns(3)
for idx, prod in enumerate(productos_filtrados):
    col_actual = cols[idx % 3]
    with col_actual:
        with st.container(border=True):
            # Imagen centrada con altura controlada
            st.image(prod['image'], width=140)
            st.markdown(f"**{prod['title'][:45]}{'...' if len(prod['title']) > 45 else ''}**")
            st.caption(f"Categoría: {prod['category'].capitalize()} | ⭐ {prod['rating']['rate']} ({prod['rating']['count']})")
            st.markdown(f"<span class='price-tag'>${float(prod['price']):,.2f} USD</span>", unsafe_allow_html=True)
            
            with st.expander("Ver descripción"):
                st.write(prod['description'])
                
            if st.button("➕ Agregar al carrito", key=f"add_{prod['id']}", use_container_width=True):
                agregar_al_carrito(prod)
                st.toast(f"Agregado: {prod['title'][:25]}...", icon="🛒")
                st.rerun()