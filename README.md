# wildfire-alphaearth-sentinel
This MVP demonstrates a multi-indicator, high-reliability wildfire detection framework that surpasses conventional approaches. By combining Earth observation with intelligent vector analytics, it opens pathways to operational-scale environmental monitoring.

# 🔥 AlphaEarth Wildfire Detection MVP

A high-precision wildfire detection and differential analysis MVP system. This project combines Google Earth Engine and AlphaEarth embedding technologies to capture multi-period satellite patterns and anticipate fire-related anomalies.

## 📦 Overview

This repository implements a three-stage wildfire detection pipeline:

1. **Satellite Image Collection & Preprocessing** (Google Earth Engine)
2. **High-dimensional Embedding Vector Generation** (AlphaEarth Foundations)
3. **Multifaceted Similarity & Anomaly Analysis** (Statistics + ML)

Target Area: 2017 California Thomas Fire (Ventura County)

## 🚀 System Structure

### 📡 Satellite Image Collection
- Source: Sentinel-2 multispectral satellite
- Resolution: 10m
- Bands: RGB + NIR
- Periods: Pre-, During-, and Post-fire timeframes
- Processing: Cloud masking, atmospheric correction, normalization

### 🔎 Embedding Generation
- Interface: AlphaEarth Foundations API
- Format: RGB image → 512D normalized vector
- Simulation fallback: Gaussian distribution for API throttling

### 🧠 Similarity & Anomaly Analysis
- Similarity Metrics: Cosine, Pearson, Spearman
- Distance Metrics: Euclidean, Manhattan, Chebyshev
- Temporal Change Analysis: Magnitude, velocity, directional shift
- Anomaly Detection: Isolation Forest, LOF, Z-score statistics
- Clustering: K-means, Hierarchical clustering
- PCA-based fire pattern extraction

## 🧪 Execution

### 🔧 Required Libraries
```bash
pip install earthengine-api numpy pandas matplotlib seaborn
pip install scikit-learn scipy requests folium
```

### 🏁 Run Instructions
```bash
jupyter notebook wildfire_alphaearth_Mvp.ipynb
```

- Execute notebook cells sequentially  
- Final dashboard displays detection results and recommended actions

## 📊 Output Format

```
🔥 Fire Probability: 0.8731 (87.31%)
⚠️ Risk Level: HIGH
📝 Decision Result: High fire possibility
🎯 Confidence: HIGH
💡 Recommended Action: Regional emergency response advised
```

## 🌍 Expansion Roadmap

- Real-time streaming support for live fire detection  
- Global wildfire monitoring network  
- Deep learning integration for predictive analytics  
- System integration with disaster response and evacuation platforms

## 🏆 Project Significance

This MVP demonstrates a **multi-indicator, high-reliability wildfire detection framework** that surpasses conventional approaches. By combining Earth observation with intelligent vector analytics, it opens pathways to operational-scale environmental monitoring.

## 📬 Contribution & Support

- Use GitHub Issues for bug reports and feature requests  
- Pull Requests are welcome!

```
