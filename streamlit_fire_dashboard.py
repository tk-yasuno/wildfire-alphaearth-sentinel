import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json
import base64
from io import BytesIO

# ページ設定
st.set_page_config(
    page_title="🔥 AlphaEarth火災検知システム",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF4B4B;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .status-high {
        background-color: #FF4444;
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
        font-weight: bold;
    }
    .status-medium {
        background-color: #FF8C00;
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
        font-weight: bold;
    }
    .status-low {
        background-color: #32CD32;
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

class StreamlitFireDashboard:
    """
    Streamlit + Foliumを使用した火災検知可視化ダッシュボード
    """
    
    def __init__(self):
        self.default_location = [34.4208, -119.6982]  # Thomas Fire中心座標
        self.fire_data = self.generate_sample_fire_data()
        
    def generate_sample_fire_data(self):
        """サンプル火災データ生成（実際の分析結果に置き換え可能）"""
        np.random.seed(42)
        
        # Thomas Fire周辺のグリッドポイント
        lat_range = np.linspace(34.35, 34.50, 10)
        lon_range = np.linspace(-119.8, -119.6, 10)
        
        data = []
        for i, lat in enumerate(lat_range):
            for j, lon in enumerate(lon_range):
                # 火災中心からの距離ベースで異常度を計算
                center_lat, center_lon = 34.4208, -119.6982
                distance = np.sqrt((lat - center_lat)**2 + (lon - center_lon)**2)
                
                # 異常度計算（中心に近いほど高い）
                anomaly_score = max(0, 1 - distance * 10) + np.random.normal(0, 0.1)
                anomaly_score = max(0, min(1, anomaly_score))
                
                # Fire/Non-fire分類
                fire_probability = anomaly_score + np.random.normal(0, 0.15)
                fire_probability = max(0, min(1, fire_probability))
                
                fire_classification = "Fire" if fire_probability > 0.6 else "Non-Fire"
                confidence = fire_probability if fire_classification == "Fire" else (1 - fire_probability)
                
                # 時系列データ生成
                periods = ['Pre-Fire', 'During-Fire', 'Post-Fire']
                period_scores = {}
                for period in periods:
                    if period == 'During-Fire':
                        period_scores[period] = anomaly_score
                    else:
                        period_scores[period] = anomaly_score * np.random.uniform(0.3, 0.7)
                
                data.append({
                    'lat': lat,
                    'lon': lon,
                    'anomaly_score': anomaly_score,
                    'fire_probability': fire_probability,
                    'fire_classification': fire_classification,
                    'confidence': confidence,
                    'grid_id': f"G_{i}_{j}",
                    **period_scores
                })
        
        return pd.DataFrame(data)
    
    def create_fire_map(self, selected_metric='anomaly_score'):
        """火災検知結果を地図上に可視化"""
        
        # 基本地図作成
        m = folium.Map(
            location=self.default_location,
            zoom_start=11,
            tiles='OpenStreetMap'
        )
        
        # 衛星画像レイヤー追加
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri',
            name='Satellite',
            overlay=False,
            control=True
        ).add_to(m)
        
        # メトリクス設定
        if selected_metric == 'anomaly_score':
            colormap = 'YlOrRd'
            popup_text = 'Anomaly Score'
        elif selected_metric == 'fire_probability':
            colormap = 'Reds'
            popup_text = 'Fire Probability'
        else:
            colormap = 'viridis'
            popup_text = selected_metric
        
        # ヒートマップデータ準備
        heat_data = []
        for _, row in self.fire_data.iterrows():
            intensity = row[selected_metric]
            heat_data.append([row['lat'], row['lon'], intensity])
        
        # ヒートマップレイヤー
        from folium.plugins import HeatMap
        HeatMap(
            heat_data,
            name=f'{popup_text} Heatmap',
            min_opacity=0.3,
            max_zoom=18,
            radius=25,
            blur=15,
            gradient={0.2: 'blue', 0.4: 'lime', 0.6: 'orange', 1: 'red'}
        ).add_to(m)
        
        # 個別ポイントマーカー
        for _, row in self.fire_data.iterrows():
            # 色分け設定
            if row['fire_classification'] == 'Fire':
                if row['confidence'] > 0.8:
                    color = 'red'
                    icon = 'fire'
                elif row['confidence'] > 0.6:
                    color = 'orange'
                    icon = 'exclamation-triangle'
                else:
                    color = 'yellow'
                    icon = 'warning'
            else:
                color = 'green'
                icon = 'check'
            
            # ポップアップ情報
            popup_html = f"""
            <div style="width: 200px;">
                <h4>🔥 {row['grid_id']}</h4>
                <b>分類:</b> {row['fire_classification']}<br>
                <b>信頼度:</b> {row['confidence']:.3f}<br>
                <b>異常度:</b> {row['anomaly_score']:.3f}<br>
                <b>火災確率:</b> {row['fire_probability']:.3f}<br>
                <b>座標:</b> ({row['lat']:.4f}, {row['lon']:.4f})<br>
                <hr>
                <b>時系列スコア:</b><br>
                • Pre-Fire: {row['Pre-Fire']:.3f}<br>
                • During-Fire: {row['During-Fire']:.3f}<br>
                • Post-Fire: {row['Post-Fire']:.3f}
            </div>
            """
            
            folium.Marker(
                location=[row['lat'], row['lon']],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"{row['grid_id']}: {row['fire_classification']} ({row['confidence']:.2f})",
                icon=folium.Icon(color=color, icon=icon, prefix='fa')
            ).add_to(m)
        
        # 凡例追加
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 200px; height: 120px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <p><b>🔥 Fire Classification Legend</b></p>
        <p><i class="fa fa-circle" style="color:red"></i> High Confidence Fire</p>
        <p><i class="fa fa-circle" style="color:orange"></i> Medium Confidence Fire</p>
        <p><i class="fa fa-circle" style="color:yellow"></i> Low Confidence Fire</p>
        <p><i class="fa fa-circle" style="color:green"></i> Non-Fire</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # レイヤーコントロール追加
        folium.LayerControl().add_to(m)
        
        return m
    
    def create_embedding_analysis_charts(self):
        """埋め込み分析結果のチャート群"""
        
        # 1. 異常度分布ヒストグラム
        fig_hist = px.histogram(
            self.fire_data, 
            x='anomaly_score',
            nbins=20,
            title='🎯 Embedding異常度分布',
            color_discrete_sequence=['#FF6B6B']
        )
        fig_hist.update_layout(
            xaxis_title='異常度スコア',
            yaxis_title='頻度',
            showlegend=False
        )
        
        # 2. Fire/Non-Fire信頼度比較
        fig_conf = px.box(
            self.fire_data,
            x='fire_classification',
            y='confidence',
            title='🔥 Fire/Non-Fire分類信頼度比較',
            color='fire_classification',
            color_discrete_map={'Fire': '#FF4444', 'Non-Fire': '#44AA44'}
        )
        fig_conf.update_layout(
            xaxis_title='分類',
            yaxis_title='信頼度'
        )
        
        # 3. 時系列変化パターン
        periods = ['Pre-Fire', 'During-Fire', 'Post-Fire']
        temporal_data = []
        for period in periods:
            for _, row in self.fire_data.iterrows():
                temporal_data.append({
                    'Period': period,
                    'Score': row[period],
                    'Classification': row['fire_classification'],
                    'Grid_ID': row['grid_id']
                })
        
        temporal_df = pd.DataFrame(temporal_data)
        fig_temporal = px.line(
            temporal_df.groupby(['Period', 'Classification'])['Score'].mean().reset_index(),
            x='Period',
            y='Score',
            color='Classification',
            title='📈 時系列変化パターン（平均値）',
            color_discrete_map={'Fire': '#FF4444', 'Non-Fire': '#44AA44'}
        )
        fig_temporal.update_layout(
            xaxis_title='期間',
            yaxis_title='スコア'
        )
        
        return fig_hist, fig_conf, fig_temporal
    
    def create_correlation_heatmap(self):
        """相関関係ヒートマップ"""
        correlation_data = self.fire_data[['anomaly_score', 'fire_probability', 'confidence', 
                                          'Pre-Fire', 'During-Fire', 'Post-Fire']].corr()
        
        fig_corr = px.imshow(
            correlation_data,
            text_auto=True,
            aspect="auto",
            title='🔗 メトリクス間相関関係',
            color_continuous_scale='RdBu_r'
        )
        fig_corr.update_layout(
            width=600,
            height=500
        )
        
        return fig_corr
    
    def create_metrics_summary(self):
        """主要メトリクス要約"""
        fire_count = len(self.fire_data[self.fire_data['fire_classification'] == 'Fire'])
        total_count = len(self.fire_data)
        fire_ratio = fire_count / total_count
        
        avg_anomaly = self.fire_data['anomaly_score'].mean()
        max_anomaly = self.fire_data['anomaly_score'].max()
        
        high_conf_fire = len(self.fire_data[
            (self.fire_data['fire_classification'] == 'Fire') & 
            (self.fire_data['confidence'] > 0.8)
        ])
        
        return {
            'fire_count': fire_count,
            'total_count': total_count,
            'fire_ratio': fire_ratio,
            'avg_anomaly': avg_anomaly,
            'max_anomaly': max_anomaly,
            'high_conf_fire': high_conf_fire
        }

def main():
    """メイン関数"""
    
    # ヘッダー
    st.markdown('<div class="main-header">🔥 AlphaEarth火災検知システム - Streamlit可視化ダッシュボード</div>', 
                unsafe_allow_html=True)
    
    # ダッシュボードインスタンス作成
    dashboard = StreamlitFireDashboard()
    
    # サイドバー設定
    st.sidebar.title("🎛️ 可視化設定")
    
    # メトリクス選択
    metric_options = {
        'anomaly_score': '🚨 Embedding異常度',
        'fire_probability': '🔥 Fire確率',
        'confidence': '🎯 信頼度'
    }
    selected_metric = st.sidebar.selectbox(
        "地図表示メトリクス",
        options=list(metric_options.keys()),
        format_func=lambda x: metric_options[x]
    )
    
    # フィルタリング設定
    st.sidebar.subheader("🔍 フィルタリング")
    
    min_anomaly = st.sidebar.slider(
        "最小異常度閾値",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.1
    )
    
    classification_filter = st.sidebar.multiselect(
        "分類フィルター",
        options=['Fire', 'Non-Fire'],
        default=['Fire', 'Non-Fire']
    )
    
    # データフィルタリング
    filtered_data = dashboard.fire_data[
        (dashboard.fire_data['anomaly_score'] >= min_anomaly) &
        (dashboard.fire_data['fire_classification'].isin(classification_filter))
    ]
    dashboard.fire_data = filtered_data
    
    # メトリクス要約
    metrics = dashboard.create_metrics_summary()
    
    # メトリクス表示
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🔥 Fire検知数",
            value=metrics['fire_count'],
            delta=f"{metrics['fire_ratio']:.1%} of total"
        )
    
    with col2:
        st.metric(
            label="🚨 平均異常度", 
            value=f"{metrics['avg_anomaly']:.3f}",
            delta=f"最大: {metrics['max_anomaly']:.3f}"
        )
    
    with col3:
        st.metric(
            label="🎯 高信頼度Fire",
            value=metrics['high_conf_fire'],
            delta=f"{metrics['high_conf_fire']/max(1, metrics['fire_count']):.1%} of fires"
        )
    
    with col4:
        st.metric(
            label="📊 総分析ポイント",
            value=metrics['total_count'],
            delta="グリッドポイント"
        )
    
    # メインコンテンツエリア
    tab1, tab2, tab3, tab4 = st.tabs(["🗺️ 地図可視化", "📊 分析チャート", "🔗 相関分析", "📋 データ詳細"])
    
    with tab1:
        st.subheader(f"🗺️ {metric_options[selected_metric]} - 地図可視化")
        
        # 地図作成・表示
        fire_map = dashboard.create_fire_map(selected_metric)
        map_data = st_folium(fire_map, width=1400, height=600)
        
        # 選択されたポイントの詳細表示
        if map_data['last_object_clicked_popup']:
            st.success("📍 選択されたポイントの詳細情報が上記ポップアップに表示されています")
    
    with tab2:
        st.subheader("📊 Embedding分析結果チャート")
        
        # チャート作成
        fig_hist, fig_conf, fig_temporal = dashboard.create_embedding_analysis_charts()
        
        # チャート表示
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig_hist, use_container_width=True)
            st.plotly_chart(fig_conf, use_container_width=True)
        
        with col2:
            st.plotly_chart(fig_temporal, use_container_width=True)
            
            # 統計サマリー
            st.subheader("📈 統計サマリー")
            st.write(dashboard.fire_data[['anomaly_score', 'fire_probability', 'confidence']].describe())
    
    with tab3:
        st.subheader("🔗 メトリクス間相関分析")
        
        # 相関ヒートマップ
        fig_corr = dashboard.create_correlation_heatmap()
        st.plotly_chart(fig_corr, use_container_width=True)
        
        # 相関分析の洞察
        st.subheader("💡 相関分析の洞察")
        st.info("""
        **主要な相関関係:**
        
        🔥 **異常度 vs Fire確率**: 強い正の相関が期待されます
        
        📈 **During-Fire vs 異常度**: 火災期間中のスコアが異常度の主要な決定要因
        
        🎯 **信頼度 vs Fire確率**: Fire分類の信頼度は確率値と密接に関連
        
        ⏰ **時系列パターン**: Pre → During → Post の変化パターンが火災の特徴を示す
        """)
    
    with tab4:
        st.subheader("📋 詳細データテーブル")
        
        # データテーブル表示
        st.dataframe(
            dashboard.fire_data.round(4),
            use_container_width=True,
            height=400
        )
        
        # CSV ダウンロード機能
        csv = dashboard.fire_data.to_csv(index=False)
        st.download_button(
            label="📥 CSVダウンロード",
            data=csv,
            file_name=f"fire_detection_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    # フッター
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center'>
        <p>🔥 <b>AlphaEarth火災検知システム</b> - Streamlit可視化ダッシュボード v1.0</p>
        <p>💡 Powered by AlphaEarth Foundations API + Streamlit + Folium</p>
        <p>📅 {}</p>
    </div>
    """.format(datetime.now().strftime("%Y年%m月%d日 %H:%M")), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
