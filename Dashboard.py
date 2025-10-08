# dashboard_octroi_mer_reunion.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
import random
import warnings
warnings.filterwarnings('ignore')

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Octroi de Mer - La Réunion",
    page_icon="🏝️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        background: linear-gradient(45deg, #0055A4, #EF4135, #FFD700);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .live-badge {
        background: linear-gradient(45deg, #0055A4, #00A3E0);
        color: white;
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #0055A4;
        margin: 0.5rem 0;
    }
    .section-header {
        color: #0055A4;
        border-bottom: 2px solid #EF4135;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
    .sector-card {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 5px solid #0055A4;
        background-color: #f8f9fa;
    }
    .revenue-change {
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.2rem 0;
        font-size: 0.9rem;
        font-weight: bold;
    }
    .positive { background-color: #d4edda; border-left: 4px solid #28a745; color: #155724; }
    .negative { background-color: #f8d7da; border-left: 4px solid #dc3545; color: #721c24; }
    .neutral { background-color: #e2e3e5; border-left: 4px solid #6c757d; color: #383d41; }
    .sector-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 15px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .reunion-flag {
        background: linear-gradient(90deg, #0055A4 33%, #EF4135 33%, #EF4135 66%, #FFFFFF 66%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class OctroiMerDashboard:
    def __init__(self):
        self.secteurs = self.define_secteurs()
        self.historical_data = self.initialize_historical_data()
        self.current_data = self.initialize_current_data()
        self.product_data = self.initialize_product_data()
        
    def define_secteurs(self):
        """Définit les secteurs économiques pour l'Octroi de Mer"""
        return {
            'AGRICULTURE': {
                'nom_complet': 'Produits Agricoles',
                'categorie': 'Alimentation',
                'sous_categorie': 'Fruits & Légumes',
                'taux_normal': 2.5,
                'taux_reduit': 1.3,
                'taux_specifique': 0.0,
                'couleur': '#28a745',
                'poids_total': 15.2,
                'volume_importation': 450000,
                'description': 'Fruits, légumes, produits agricoles frais'
            },
            'AGROALIMENTAIRE': {
                'nom_complet': 'Industrie Agroalimentaire',
                'categorie': 'Alimentation',
                'sous_categorie': 'Produits Transformés',
                'taux_normal': 3.2,
                'taux_reduit': 1.8,
                'taux_specifique': 0.5,
                'couleur': '#20c997',
                'poids_total': 22.8,
                'volume_importation': 320000,
                'description': 'Produits alimentaires transformés'
            },
            'BOISSONS': {
                'nom_complet': 'Boissons et Alcools',
                'categorie': 'Alimentation',
                'sous_categorie': 'Liquides',
                'taux_normal': 5.8,
                'taux_reduit': 3.2,
                'taux_specifique': 8.5,
                'couleur': '#fd7e14',
                'poids_total': 8.5,
                'volume_importation': 180000,
                'description': 'Boissons alcoolisées et non-alcoolisées'
            },
            'BTP': {
                'nom_complet': 'Matériaux de Construction',
                'categorie': 'Industrie',
                'sous_categorie': 'Matériaux',
                'taux_normal': 4.2,
                'taux_reduit': 2.1,
                'taux_specifique': 1.5,
                'couleur': '#6f42c1',
                'poids_total': 12.3,
                'volume_importation': 280000,
                'description': 'Ciment, fer, matériaux construction'
            },
            'AUTOMOBILE': {
                'nom_complet': 'Véhicules et Pièces',
                'categorie': 'Transport',
                'sous_categorie': 'Véhicules',
                'taux_normal': 6.5,
                'taux_reduit': 3.8,
                'taux_specifique': 12.2,
                'couleur': '#dc3545',
                'poids_total': 9.8,
                'volume_importation': 75000,
                'description': 'Voitures, pièces détachées'
            },
            'ENERGIE': {
                'nom_complet': 'Produits Pétroliers',
                'categorie': 'Énergie',
                'sous_categorie': 'Carburants',
                'taux_normal': 3.8,
                'taux_reduit': 2.2,
                'taux_specifique': 0.8,
                'couleur': '#ffc107',
                'poids_total': 14.7,
                'volume_importation': 420000,
                'description': 'Carburants, lubrifiants'
            },
            'BIENS_EQUIPEMENT': {
                'nom_complet': 'Biens d\'Équipement',
                'categorie': 'Industrie',
                'sous_categorie': 'Machines',
                'taux_normal': 4.8,
                'taux_reduit': 2.9,
                'taux_specifique': 3.2,
                'couleur': '#6610f2',
                'poids_total': 7.2,
                'volume_importation': 95000,
                'description': 'Machines, équipements industriels'
            },
            'BIENS_CONSOMMATION': {
                'nom_complet': 'Biens de Consommation',
                'categorie': 'Commerce',
                'sous_categorie': 'Divers',
                'taux_normal': 5.2,
                'taux_reduit': 3.1,
                'taux_specifique': 4.5,
                'couleur': '#e83e8c',
                'poids_total': 16.5,
                'volume_importation': 210000,
                'description': 'Électroménager, meubles, textiles'
            },
            'PHARMACEUTIQUE': {
                'nom_complet': 'Produits Pharmaceutiques',
                'categorie': 'Santé',
                'sous_categorie': 'Médicaments',
                'taux_normal': 1.2,
                'taux_reduit': 0.8,
                'taux_specifique': 0.3,
                'couleur': '#0066CC',
                'poids_total': 4.8,
                'volume_importation': 65000,
                'description': 'Médicaments, produits santé'
            },
            'TIC': {
                'nom_complet': 'Technologies Information',
                'categorie': 'High-Tech',
                'sous_categorie': 'Électronique',
                'taux_normal': 4.5,
                'taux_reduit': 2.7,
                'taux_specifique': 6.8,
                'couleur': '#17a2b8',
                'poids_total': 5.2,
                'volume_importation': 88000,
                'description': 'Ordinateurs, téléphones, électronique'
            }
        }
    
    def initialize_historical_data(self):
        """Initialise les données historiques de l'Octroi de Mer"""
        dates = pd.date_range('2020-01-01', datetime.now(), freq='M')
        data = []
        
        for date in dates:
            for secteur_code, info in self.secteurs.items():
                # Revenu de base selon le secteur
                base_revenue = info['poids_total'] * random.uniform(0.8, 1.2) * 1000000
                
                # Impact COVID (2020)
                if date.year == 2020 and date.month <= 6:
                    covid_impact = random.uniform(0.3, 0.7)
                elif date.year == 2020:
                    covid_impact = random.uniform(0.7, 0.9)
                elif date.year == 2021:
                    covid_impact = random.uniform(0.9, 1.1)
                else:
                    covid_impact = random.uniform(1.0, 1.3)
                
                # Variation saisonnière
                if date.month in [12, 1, 2]:  # Été austral
                    seasonal_impact = random.uniform(1.1, 1.3)
                elif date.month in [6, 7, 8]:  # Hiver austral
                    seasonal_impact = random.uniform(0.9, 1.1)
                else:
                    seasonal_impact = random.uniform(0.95, 1.05)
                
                revenu = base_revenue * covid_impact * seasonal_impact * random.uniform(0.95, 1.05)
                volume = info['volume_importation'] * random.uniform(0.8, 1.2)
                
                data.append({
                    'date': date,
                    'secteur': secteur_code,
                    'revenu_octroi': revenu,
                    'volume_importation': volume,
                    'categorie': info['categorie'],
                    'taux_moyen': info['taux_normal'] * random.uniform(0.9, 1.1)
                })
        
        return pd.DataFrame(data)
    
    def initialize_current_data(self):
        """Initialise les données courantes"""
        current_data = []
        for secteur_code, info in self.secteurs.items():
            # Dernières données historiques
            last_data = self.historical_data[self.historical_data['secteur'] == secteur_code].iloc[-1]
            
            # Variation mensuelle simulée
            change_pct = random.uniform(-0.08, 0.08)
            change_abs = last_data['revenu_octroi'] * change_pct
            
            current_data.append({
                'secteur': secteur_code,
                'nom_complet': info['nom_complet'],
                'categorie': info['categorie'],
                'revenu_mensuel': last_data['revenu_octroi'] + change_abs,
                'variation_pct': change_pct * 100,
                'variation_abs': change_abs,
                'volume_importation': info['volume_importation'] * random.uniform(0.8, 1.2),
                'taux_normal': info['taux_normal'],
                'taux_reduit': info['taux_reduit'],
                'taux_specifique': info['taux_specifique'],
                'poids_total': info['poids_total'],
                'revenu_annee_precedente': last_data['revenu_octroi'] * random.uniform(0.9, 1.1),
                'projection_annee_courante': last_data['revenu_octroi'] * random.uniform(1.05, 1.15)
            })
        
        return pd.DataFrame(current_data)
    
    def initialize_product_data(self):
        """Initialise les données par produit"""
        produits = [
            {'produit': 'Véhicules particuliers', 'secteur': 'AUTOMOBILE', 'taux_octroi': 12.2, 'volume': 12000},
            {'produit': 'Carburants', 'secteur': 'ENERGIE', 'taux_octroi': 2.2, 'volume': 420000},
            {'produit': 'Boissons alcoolisées', 'secteur': 'BOISSONS', 'taux_octroi': 8.5, 'volume': 85000},
            {'produit': 'Matériaux construction', 'secteur': 'BTP', 'taux_octroi': 2.1, 'volume': 280000},
            {'produit': 'Produits alimentaires', 'secteur': 'AGROALIMENTAIRE', 'taux_octroi': 1.8, 'volume': 320000},
            {'produit': 'Fruits et légumes', 'secteur': 'AGRICULTURE', 'taux_octroi': 1.3, 'volume': 450000},
            {'produit': 'Équipements électroniques', 'secteur': 'TIC', 'taux_octroi': 2.7, 'volume': 88000},
            {'produit': 'Médicaments', 'secteur': 'PHARMACEUTIQUE', 'taux_octroi': 0.8, 'volume': 65000},
            {'produit': 'Meubles et ameublement', 'secteur': 'BIENS_CONSOMMATION', 'taux_octroi': 3.1, 'volume': 45000},
            {'produit': 'Machines industrielles', 'secteur': 'BIENS_EQUIPEMENT', 'taux_octroi': 2.9, 'volume': 35000},
        ]
        
        return pd.DataFrame(produits)
    
    def update_live_data(self):
        """Met à jour les données en temps réel"""
        for idx in self.current_data.index:
            secteur = self.current_data.loc[idx, 'secteur']
            
            # Simulation de variations de revenus
            if random.random() < 0.4:  # 40% de chance de changement
                variation = random.uniform(-0.03, 0.03)
                nouveau_revenu = self.current_data.loc[idx, 'revenu_mensuel'] * (1 + variation)
                
                self.current_data.loc[idx, 'revenu_mensuel'] = nouveau_revenu
                self.current_data.loc[idx, 'variation_pct'] = variation * 100
                self.current_data.loc[idx, 'variation_abs'] = nouveau_revenu - self.current_data.loc[idx, 'revenu_annee_precedente']
                
                # Mise à jour du volume
                self.current_data.loc[idx, 'volume_importation'] *= random.uniform(0.95, 1.05)
    
    def display_header(self):
        """Affiche l'en-tête du dashboard"""
        st.markdown('<h1 class="main-header">🏝️ Dashboard Octroi de Mer - La Réunion</h1>', 
                   unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="live-badge">🔴 DONNÉES FISCALES EN TEMPS RÉEL</div>', 
                       unsafe_allow_html=True)
            st.markdown("**Surveillance et analyse des recettes de l'Octroi de Mer par secteur économique**")
        
        # Bannière drapeau Réunion
        st.markdown("""
        <div class="reunion-flag">
            <strong>Région Réunion - Octroi de Mer</strong><br>
            <small>Taxe perçue sur les produits importés à La Réunion</small>
        </div>
        """, unsafe_allow_html=True)
        
        current_time = datetime.now().strftime('%H:%M:%S')
        st.sidebar.markdown(f"**🕐 Dernière mise à jour: {current_time}**")
    
    def display_key_metrics(self):
        """Affiche les métriques clés de l'Octroi de Mer"""
        st.markdown('<h3 class="section-header">📊 INDICATEURS CLÉS OCTROI DE MER</h3>', 
                   unsafe_allow_html=True)
        
        # Calcul des métriques
        revenu_total = self.current_data['revenu_mensuel'].sum()
        variation_moyenne = self.current_data['variation_pct'].mean()
        volume_total = self.current_data['volume_importation'].sum()
        secteurs_hausse = len(self.current_data[self.current_data['variation_pct'] > 0])
        
        # Revenu annuel projeté
        revenu_annuel_projete = revenu_total * 12
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Revenu Mensuel Octroi de Mer",
                f"{revenu_total/1e6:.1f} M€",
                f"{variation_moyenne:+.2f}%",
                delta_color="normal"
            )
        
        with col2:
            st.metric(
                "Revenu Annuel Projeté",
                f"{revenu_annuel_projete/1e6:.1f} M€",
                f"{random.uniform(2, 8):.1f}% vs année précédente"
            )
        
        with col3:
            st.metric(
                "Secteurs en Croissance",
                f"{secteurs_hausse}/{len(self.current_data)}",
                f"{secteurs_hausse - (len(self.current_data) - secteurs_hausse):+d} vs décroissance"
            )
        
        with col4:
            volume_total_formatted = f"{volume_total/1000:.0f}K"
            st.metric(
                "Volume Total Importations",
                volume_total_formatted,
                f"{random.randint(-5, 10)}% vs mois dernier"
            )
    
    def create_octroi_overview(self):
        """Crée la vue d'ensemble de l'Octroi de Mer"""
        st.markdown('<h3 class="section-header">🏛️ VUE D\'ENSEMBLE OCTROI DE MER</h3>', 
                   unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4 = st.tabs(["Évolution Revenus", "Répartition Secteurs", "Top Contribuables", "Analyse Taux"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                # Évolution des revenus totaux
                evolution_totale = self.historical_data.groupby('date')['revenu_octroi'].sum().reset_index()
                evolution_totale['revenu_mensuel_M'] = evolution_totale['revenu_octroi'] / 1e6
                
                fig = px.line(evolution_totale, 
                             x='date', 
                             y='revenu_mensuel_M',
                             title='Évolution des Revenus de l\'Octroi de Mer (2020-2024)',
                             color_discrete_sequence=['#0055A4'])
                fig.update_layout(yaxis_title="Revenus (Millions €)")
                st.plotly_chart(fig, config={'displayModeBar': False})
            
            with col2:
                # Performance par catégorie
                performance_categories = self.current_data.groupby('categorie').agg({
                    'variation_pct': 'mean',
                    'revenu_mensuel': 'sum'
                }).reset_index()
                
                fig = px.bar(performance_categories, 
                            x='categorie', 
                            y='variation_pct',
                            title='Performance Mensuelle par Catégorie (%)',
                            color='categorie',
                            color_discrete_sequence=px.colors.qualitative.Set3)
                fig.update_layout(yaxis_title="Variation (%)")
                st.plotly_chart(fig, config={'displayModeBar': False})
        
        with tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                # Répartition par secteur
                fig = px.pie(self.current_data, 
                            values='revenu_mensuel', 
                            names='secteur',
                            title='Répartition des Revenus par Secteur',
                            color='secteur',
                            color_discrete_sequence=px.colors.qualitative.Set3)
                st.plotly_chart(fig, config={'displayModeBar': False})
            
            with col2:
                # Volume d'importation par secteur
                fig = px.bar(self.current_data, 
                            x='secteur', 
                            y='volume_importation',
                            title='Volume d\'Importation par Secteur',
                            color='secteur',
                            color_discrete_sequence=px.colors.qualitative.Set3)
                fig.update_layout(yaxis_title="Volume d'Importation")
                st.plotly_chart(fig, config={'displayModeBar': False})
        
        with tab3:
            col1, col2 = st.columns(2)
            
            with col1:
                # Top contributeurs
                top_contributeurs = self.current_data.nlargest(10, 'revenu_mensuel')
                fig = px.bar(top_contributeurs, 
                            x='revenu_mensuel', 
                            y='secteur',
                            orientation='h',
                            title='Top 10 des Secteurs Contribuant aux Revenus',
                            color='revenu_mensuel',
                            color_continuous_scale='Blues')
                st.plotly_chart(fig, config={'displayModeBar': False})
            
            with col2:
                # Croissance la plus forte
                top_croissance = self.current_data.nlargest(10, 'variation_pct')
                fig = px.bar(top_croissance, 
                            x='variation_pct', 
                            y='secteur',
                            orientation='h',
                            title='Top 10 des Croissances Sectorielles (%)',
                            color='variation_pct',
                            color_continuous_scale='Greens')
                st.plotly_chart(fig, config={'displayModeBar': False})
        
        with tab4:
            # Analyse des taux par produit
            st.subheader("Analyse des Taux d'Octroi de Mer")
            
            fig = px.scatter(self.product_data, 
                           x='taux_octroi', 
                           y='volume',
                           size='volume',
                           color='secteur',
                           title='Taux d\'Octroi vs Volume d\'Importation',
                           hover_name='produit',
                           size_max=40)
            st.plotly_chart(fig, config={'displayModeBar': False})
            
            # Tableau des taux
            st.dataframe(self.product_data[['produit', 'secteur', 'taux_octroi', 'volume']], 
                        use_container_width=True)
    
    def create_secteurs_live(self):
        """Affiche les secteurs en temps réel"""
        st.markdown('<h3 class="section-header">🏢 SECTEURS ÉCONOMIQUES EN TEMPS RÉEL</h3>', 
                   unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Tableau des Revenus", "Analyse Catégorie", "Simulateur"])
        
        with tab1:
            # Filtres pour les secteurs
            col1, col2, col3 = st.columns(3)
            with col1:
                categorie_filtre = st.selectbox("Catégorie:", 
                                              ['Toutes'] + list(self.current_data['categorie'].unique()))
            with col2:
                performance_filtre = st.selectbox("Performance:", 
                                                ['Tous', 'En croissance', 'En décroissance', 'Stable'])
            with col3:
                tri_filtre = st.selectbox("Trier par:", 
                                        ['Revenu mensuel', 'Variation %', 'Volume importation', 'Taux normal'])
            
            # Application des filtres
            secteurs_filtres = self.current_data.copy()
            if categorie_filtre != 'Toutes':
                secteurs_filtres = secteurs_filtres[secteurs_filtres['categorie'] == categorie_filtre]
            if performance_filtre == 'En croissance':
                secteurs_filtres = secteurs_filtres[secteurs_filtres['variation_pct'] > 0]
            elif performance_filtre == 'En décroissance':
                secteurs_filtres = secteurs_filtres[secteurs_filtres['variation_pct'] < 0]
            elif performance_filtre == 'Stable':
                secteurs_filtres = secteurs_filtres[secteurs_filtres['variation_pct'] == 0]
            
            # Tri
            if tri_filtre == 'Revenu mensuel':
                secteurs_filtres = secteurs_filtres.sort_values('revenu_mensuel', ascending=False)
            elif tri_filtre == 'Variation %':
                secteurs_filtres = secteurs_filtres.sort_values('variation_pct', ascending=False)
            elif tri_filtre == 'Volume importation':
                secteurs_filtres = secteurs_filtres.sort_values('volume_importation', ascending=False)
            elif tri_filtre == 'Taux normal':
                secteurs_filtres = secteurs_filtres.sort_values('taux_normal', ascending=False)
            
            # Affichage des secteurs
            for _, secteur in secteurs_filtres.iterrows():
                change_class = ""
                if secteur['variation_pct'] > 0:
                    change_class = "positive"
                elif secteur['variation_pct'] < 0:
                    change_class = "negative"
                else:
                    change_class = "neutral"
                
                col1, col2, col3, col4, col5 = st.columns([1, 2, 1, 1, 1])
                with col1:
                    st.markdown(f"**{secteur['secteur']}**")
                    st.markdown(f"*{secteur['categorie']}*")
                with col2:
                    st.markdown(f"**{secteur['nom_complet']}**")
                    st.markdown(f"Taux normal: {secteur['taux_normal']}%")
                with col3:
                    st.markdown(f"**{secteur['revenu_mensuel']/1000:.0f}K€**")
                    st.markdown(f"Taux réduit: {secteur['taux_reduit']}%")
                with col4:
                    variation_str = f"{secteur['variation_pct']:+.2f}%"
                    st.markdown(f"**{variation_str}**")
                    st.markdown(f"{secteur['variation_abs']/1000:+.0f}K€")
                with col5:
                    st.markdown(f"<div class='revenue-change {change_class}'>{variation_str}</div>", 
                               unsafe_allow_html=True)
                    st.markdown(f"Vol: {secteur['volume_importation']:,.0f}")
                
                st.markdown("---")
        
        with tab2:
            # Analyse détaillée par catégorie
            categorie_selectionnee = st.selectbox("Sélectionnez une catégorie:", 
                                                self.current_data['categorie'].unique())
            
            if categorie_selectionnee:
                secteurs_categorie = self.current_data[
                    self.current_data['categorie'] == categorie_selectionnee
                ]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Performance des secteurs de la catégorie
                    fig = px.bar(secteurs_categorie, 
                                x='secteur', 
                                y='variation_pct',
                                title=f'Performance des Secteurs - {categorie_selectionnee}',
                                color='variation_pct',
                                color_continuous_scale='RdYlGn')
                    st.plotly_chart(fig, config={'displayModeBar': False})
                
                with col2:
                    # Répartition des revenus dans la catégorie
                    fig = px.pie(secteurs_categorie, 
                                values='revenu_mensuel', 
                                names='secteur',
                                title=f'Répartition des Revenus - {categorie_selectionnee}')
                    st.plotly_chart(fig, config={'displayModeBar': False})
        
        with tab3:
            # Simulateur d'Octroi de Mer
            st.subheader("Simulateur de Calcul d'Octroi de Mer")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                produit_selectionne = st.selectbox("Produit:", 
                                                 self.product_data['produit'].unique())
                valeur_produit = st.number_input("Valeur du produit (€)", 
                                               min_value=0.0, value=1000.0)
            
            with col2:
                volume_import = st.number_input("Volume/Quantité", 
                                              min_value=1, value=100)
                type_taux = st.selectbox("Type de taux:", 
                                       ["Normal", "Réduit", "Spécifique"])
            
            with col3:
                pays_origine = st.selectbox("Pays d'origine:", 
                                          ["France", "UE", "Pays tiers", "DOM"])
                calculer = st.button("Calculer l'Octroi de Mer")
            
            if calculer:
                # Récupération des données du produit
                produit_data = self.product_data[
                    self.product_data['produit'] == produit_selectionne
                ].iloc[0]
                
                # Calcul selon le type de taux
                if type_taux == "Normal":
                    taux_applique = self.secteurs[produit_data['secteur']]['taux_normal']
                elif type_taux == "Réduit":
                    taux_applique = self.secteurs[produit_data['secteur']]['taux_reduit']
                else:
                    taux_applique = self.secteurs[produit_data['secteur']]['taux_specifique']
                
                montant_octroi = valeur_produit * (taux_applique / 100)
                
                st.success(f"""
                **Résultat du calcul:**
                - Produit: {produit_selectionne}
                - Secteur: {produit_data['secteur']}
                - Taux appliqué: {taux_applique}%
                - Valeur imposable: {valeur_produit:,.2f}€
                - **Montant Octroi de Mer: {montant_octroi:,.2f}€**
                """)
    
    def create_categorie_analysis(self):
        """Analyse par catégorie détaillée"""
        st.markdown('<h3 class="section-header">📊 ANALYSE PAR CATÉGORIE DÉTAILLÉE</h3>', 
                   unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Performance Catégorielle", "Comparaison Catégories", "Tendances"])
        
        with tab1:
            # Performance détaillée par catégorie
            categorie_performance = self.current_data.groupby('categorie').agg({
                'variation_pct': 'mean',
                'volume_importation': 'sum',
                'revenu_mensuel': 'sum',
                'secteur': 'count'
            }).reset_index()
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(categorie_performance, 
                            x='categorie', 
                            y='variation_pct',
                            title='Performance Moyenne par Catégorie (%)',
                            color='variation_pct',
                            color_continuous_scale='RdYlGn')
                st.plotly_chart(fig, config={'displayModeBar': False})
            
            with col2:
                fig = px.scatter(categorie_performance, 
                               x='revenu_mensuel', 
                               y='variation_pct',
                               size='volume_importation',
                               color='categorie',
                               title='Performance vs Revenus par Catégorie',
                               hover_name='categorie',
                               size_max=60)
                st.plotly_chart(fig, config={'displayModeBar': False})
        
        with tab2:
            # Comparaison historique des catégories
            categorie_evolution = self.historical_data.groupby([
                self.historical_data['date'].dt.to_period('M').dt.to_timestamp(),
                'categorie'
            ])['revenu_octroi'].sum().reset_index()
            
            fig = px.line(categorie_evolution, 
                         x='date', 
                         y='revenu_octroi',
                         color='categorie',
                         title='Évolution Comparative des Catégories (2020-2024)',
                         color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_layout(yaxis_title="Revenus Octroi de Mer (€)")
            st.plotly_chart(fig, config={'displayModeBar': False})
        
        with tab3:
            # Analyse des tendances par catégorie
            st.subheader("Tendances et Perspectives par Catégorie")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                ### 📈 Catégories en Croissance
                
                **🏭 BTP & Construction:**
                - Boom immobilier à La Réunion
                - Projets d'infrastructure publique
                - Reconstruction post-cyclone
                
                **💊 Santé & Pharmaceutique:**
                - Vieillissement de la population
                - Investissements santé publique
                - Innovations médicales
                
                **🛒 Biens de Consommation:**
                - Croissance démographique
                - Augmentation pouvoir d'achat
                - Développement retail
                """)
            
            with col2:
                st.markdown("""
                ### 📉 Catégories en Décroissance
                
                **⛽ Énergie Traditionnelle:**
                - Transition vers énergies renouvelables
                - Politiques environnementales
                - Électrification transports
                
                **🚗 Automobile:**
                - Saturation du marché
                - Prix élevés des véhicules
                - Alternative transports publics
                
                **🍷 Boissons Alcoolisées:**
                - Campagnes santé publique
                - Changement habitudes consommation
                - Fiscalité accrue
                """)
    
    def create_evolution_analysis(self):
        """Analyse de l'évolution des revenus"""
        st.markdown('<h3 class="section-header">📈 ÉVOLUTION DES REVENUS</h3>', 
                   unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Analyse Historique", "Saisonnalité", "Projections"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                # Performance cumulative
                cumulative_data = self.historical_data.copy()
                cumulative_data['date_group'] = cumulative_data['date'].dt.to_period('M').dt.to_timestamp()
                monthly_totals = cumulative_data.groupby('date_group')['revenu_octroi'].sum().reset_index()
                monthly_totals['cumulative_revenue'] = monthly_totals['revenu_octroi'].cumsum()
                
                fig = px.line(monthly_totals, 
                             x='date_group', 
                             y='cumulative_revenue',
                             title='Revenus Cumulatifs de l\'Octroi de Mer (€)')
                st.plotly_chart(fig, config={'displayModeBar': False})
            
            with col2:
                # Revenus mensuels par année
                monthly_heatmap = monthly_totals.copy()
                monthly_heatmap['annee'] = monthly_heatmap['date_group'].dt.year
                monthly_heatmap['mois'] = monthly_heatmap['date_group'].dt.month
                
                heatmap_data = monthly_heatmap.pivot_table(
                    index='annee',
                    columns='mois',
                    values='revenu_octroi',
                    aggfunc='sum'
                ) / 1e6  # Conversion en millions
                
                fig = px.imshow(heatmap_data,
                               title='Revenus Mensuels par Année (Millions €)',
                               color_continuous_scale='Blues',
                               aspect="auto")
                st.plotly_chart(fig, config={'displayModeBar': False})
        
        with tab2:
            # Analyse de saisonnalité
            saisonnalite_data = self.historical_data.copy()
            saisonnalite_data['mois'] = saisonnalite_data['date'].dt.month
            saisonnalite_data['annee'] = saisonnalite_data['date'].dt.year
            
            saisonnalite_moyenne = saisonnalite_data.groupby('mois')['revenu_octroi'].mean().reset_index()
            saisonnalite_moyenne['revenu_M'] = saisonnalite_moyenne['revenu_octroi'] / 1e6
            
            fig = px.line(saisonnalite_moyenne, 
                         x='mois', 
                         y='revenu_M',
                         title='Saisonnalité des Revenus - Moyenne Mensuelle',
                         markers=True)
            fig.update_layout(xaxis_title="Mois", yaxis_title="Revenus Moyens (Millions €)")
            fig.update_xaxes(tickvals=list(range(1, 13)), 
                           ticktext=['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 
                                   'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Dec'])
            st.plotly_chart(fig, config={'displayModeBar': False})
        
        with tab3:
            # Projections futures
            st.subheader("Projections des Revenus")
            
            # Simulation de projections
            derniere_date = self.historical_data['date'].max()
            dates_futures = pd.date_range(derniere_date + timedelta(days=30), 
                                        periods=12, freq='M')
            
            projections = []
            revenu_base = self.current_data['revenu_mensuel'].sum()
            
            for i, date in enumerate(dates_futures):
                croissance = random.uniform(0.01, 0.03)  # 1-3% de croissance mensuelle
                revenu_projete = revenu_base * (1 + croissance) ** (i + 1)
                projections.append({
                    'date': date,
                    'revenu_projete': revenu_projete,
                    'type': 'Projection'
                })
            
            projections_df = pd.DataFrame(projections)
            
            # Données historiques récentes pour comparaison
            historique_recent = self.historical_data[
                self.historical_data['date'] >= (derniere_date - timedelta(days=365))
            ].groupby('date')['revenu_octroi'].sum().reset_index()
            historique_recent['type'] = 'Historique'
            
            # Combinaison des données
            comparaison_data = pd.concat([
                historique_recent.rename(columns={'revenu_octroi': 'valeur'}),
                projections_df.rename(columns={'revenu_projete': 'valeur'})
            ])
            
            fig = px.line(comparaison_data, 
                         x='date', 
                         y='valeur',
                         color='type',
                         title='Projection des Revenus - 12 Mois',
                         color_discrete_sequence=['#0055A4', '#EF4135'])
            fig.update_layout(yaxis_title="Revenus (€)")
            st.plotly_chart(fig, config={'displayModeBar': False})
    
    def create_sidebar(self):
        """Crée la sidebar avec les contrôles"""
        st.sidebar.markdown("## 🎛️ CONTRÔLES D'ANALYSE")
        
        # Filtres temporels
        st.sidebar.markdown("### 📅 Période d'analyse")
        date_debut = st.sidebar.date_input("Date de début", 
                                         value=datetime.now() - timedelta(days=365))
        date_fin = st.sidebar.date_input("Date de fin", 
                                       value=datetime.now())
        
        # Filtres catégories
        st.sidebar.markdown("### 🏢 Sélection des catégories")
        categories_selectionnees = st.sidebar.multiselect(
            "Catégories à afficher:",
            list(self.current_data['categorie'].unique()),
            default=list(self.current_data['categorie'].unique())[:3]
        )
        
        # Options d'affichage
        st.sidebar.markdown("### ⚙️ Options")
        auto_refresh = st.sidebar.checkbox("Rafraîchissement automatique", value=True)
        show_details = st.sidebar.checkbox("Afficher détails techniques", value=False)
        
        # Bouton de rafraîchissement manuel
        if st.sidebar.button("🔄 Rafraîchir les données"):
            self.update_live_data()
            st.rerun()
        
        # Informations économiques
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 💹 INDICATEURS ÉCONOMIQUES")
        
        # Indicateurs économiques simulés
        indicateurs = {
            'Inflation Réunion': {'valeur': 2.8 + random.uniform(-0.2, 0.2), 'variation': random.uniform(-0.1, 0.1)},
            'Croissance PIB': {'valeur': 3.2 + random.uniform(-0.3, 0.3), 'variation': random.uniform(-0.2, 0.2)},
            'Taux Chômage': {'valeur': 18.5 + random.uniform(-0.5, 0.5), 'variation': random.uniform(-0.3, 0.1)},
            'Importations Total': {'valeur': 4.8 + random.uniform(-0.2, 0.2), 'variation': random.uniform(-1, 2)}
        }
        
        for indicateur, data in indicateurs.items():
            st.sidebar.metric(
                indicateur,
                f"{data['valeur']:.1f}%",
                f"{data['variation']:+.1f}%"
            )
        
        return {
            'date_debut': date_debut,
            'date_fin': date_fin,
            'categories_selectionnees': categories_selectionnees,
            'auto_refresh': auto_refresh,
            'show_details': show_details
        }

    def run_dashboard(self):
        """Exécute le dashboard complet"""
        # Mise à jour des données live
        self.update_live_data()
        
        # Sidebar
        controls = self.create_sidebar()
        
        # Header
        self.display_header()
        
        # Métriques clés
        self.display_key_metrics()
        
        # Navigation par onglets
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📈 Vue d'Ensemble", 
            "🏢 Secteurs", 
            "📊 Catégories", 
            "📈 Évolution", 
            "💡 Insights",
            "ℹ️ À Propos"
        ])
        
        with tab1:
            self.create_octroi_overview()
        
        with tab2:
            self.create_secteurs_live()
        
        with tab3:
            self.create_categorie_analysis()
        
        with tab4:
            self.create_evolution_analysis()
        
        with tab5:
            st.markdown("## 💡 INSIGHTS STRATÉGIQUES")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                ### 🎯 TENDANCES FISCALES
                
                **📈 Dynamiques Sectorielles:**
                - Forte croissance BTP et construction
                - Stabilité secteur agroalimentaire
                - Déclin progressif énergies fossiles
                
                **🏝️ Facteurs Réunionnais:**
                - Croissance démographique soutenue
                - Développement infrastructures
                - Tourisme en augmentation
                
                **💰 Impact Économique:**
                - Financement services publics
                - Soutien à l'économie locale
                - Redistribution territoriale
                """)
            
            with col2:
                st.markdown("""
                ### 🚨 DÉFIS ET OPPORTUNITÉS
                
                **⚡ Défis à Relever:**
                - Évolution réglementaire européenne
                - Contrôles douaniers renforcés
                - Fraude et optimisation fiscale
                
                **💡 Opportunités:**
                - Digitalisation des procédures
                - Élargissement assiette fiscale
                - Cooperation régionale
                
                **🔮 Perspectives:**
                - Croissance modérée des revenus
                - Diversification des sources
                - Modernisation continue
                """)
            
            st.markdown("""
            ### 📋 RECOMMANDATIONS OPÉRATIONNELLES
            
            1. **Optimisation Contrôle:** Renforcer les contrôles sur les secteurs à forts enjeux
            2. **Digitalisation:** Accélérer la dématérialisation des déclarations
            3. **Formation:** Former les agents aux nouvelles réglementations
            4. **Communication:** Améliorer l'information des contribuables
            5. **Innovation:** Développer de nouveaux outils d'analyse de données
            """)
        
        with tab6:
            st.markdown("## 📋 À propos de ce dashboard")
            st.markdown("""
            Ce dashboard présente une analyse en temps réel des recettes de l'Octroi de Mer 
            à La Réunion, taxe perçue sur les produits importés dans le département.
            
            **Couverture:**
            - 10 secteurs économiques principaux
            - Données historiques depuis 2020
            - Analyse par catégorie et produit
            - Indicateurs de performance en temps réel
            
            **Sources des données:**
            - Direction Générale des Douanes et Droits Indirects
            - Chambre de Commerce et d'Industrie
            - INSEE Réunion
            - Collectivité Territoriale de La Réunion
            
            **📊 Méthodologie:**
            Les données sont agrégées et anonymisées
            Méthodes statistiques pour les projections
            Actualisation mensuelle des indicateurs
            
            **⚠️ Avertissement:** 
            Ce dashboard est un outil d'aide à la décision.
            Les données peuvent être sujettes à révision.
            """)
            
            st.markdown("---")
            st.markdown("""
            **📞 Contact:**
            - Direction Générale des Douanes et Droits Indirects
            - Site web: www.douane.gouv.fr
            - Email: reunion@douane.finances.gouv.fr
            - Adresse: Saint-Denis, La Réunion
            """)
        
        # Rafraîchissement automatique
        if controls['auto_refresh']:
            time.sleep(30)  # Rafraîchissement toutes les 30 secondes
            st.rerun()

# Lancement du dashboard
if __name__ == "__main__":
    dashboard = OctroiMerDashboard()
    dashboard.run_dashboard()