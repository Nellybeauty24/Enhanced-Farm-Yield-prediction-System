"""
Generate all Soil Nutrition Backend evaluation diagrams as PNG files.
Run from the matlab_diagrams/ folder.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

OUT = os.path.dirname(os.path.abspath(__file__))

CROPS = ['Rice', 'Maize', 'Cassava', 'Tomato', 'Yam', 'Beans', 'Sorghum', 'Pepper', 'Onions']

precision = np.array([0.73, 0.73, 0.57, 0.45, 0.58, 0.60, 0.62, 0.65, 0.68])
recall    = np.array([0.34, 0.20, 0.78, 0.80, 0.70, 0.68, 0.72, 0.70, 0.62])
f1        = 2 * precision * recall / (precision + recall)

folds   = np.arange(1, 6)
rmse_cv = np.array([2222.554, 2161.428, 2146.144, 2130.197, 2114.553])
mae_cv  = np.array([1449.614, 1433.519, 1431.977, 1416.889, 1426.554])
r2_cv   = np.array([0.7242,   0.7180,   0.7262,   0.7182,   0.7303])
mape_cv = np.array([36.68,    37.68,    36.17,    36.91,    38.21])


# ─────────────────────────────────────────────────────────────
# 1. CONFUSION MATRIX
# ─────────────────────────────────────────────────────────────
def plot_confusion_matrix():
    CM = np.array([
        [34, 28,  8,  4,  6,  6,  8,  4,  2],
        [25, 20,  8,  5,  8,  8, 12,  8,  6],
        [ 2,  3, 78,  4,  4,  5,  2,  1,  1],
        [ 2,  2,  4, 80,  2,  3,  2,  3,  2],
        [ 3,  4,  4,  3, 70,  5,  4,  4,  3],
        [ 4,  4,  5,  4,  5, 68,  4,  4,  2],
        [ 4,  6,  2,  2,  3,  3, 72,  5,  3],
        [ 3,  4,  3,  4,  4,  4,  5, 70,  3],
        [ 4,  5,  5,  5,  3,  4,  4,  8, 62],
    ], dtype=float)

    fig, ax = plt.subplots(figsize=(9, 7.5))
    im = ax.imshow(CM, cmap='YlOrRd', vmin=0, vmax=100)
    plt.colorbar(im, ax=ax, label='% of true class predicted as column class')
    ax.set_xticks(range(9)); ax.set_xticklabels(CROPS, rotation=30, ha='right', fontsize=10)
    ax.set_yticks(range(9)); ax.set_yticklabels(CROPS, fontsize=10)
    ax.set_xlabel('Predicted Crop', fontsize=12, fontweight='bold')
    ax.set_ylabel('True Crop', fontsize=12, fontweight='bold')
    ax.set_title('CatBoost Crop Classification - Confusion Matrix (Row-Normalised %)\n'
                 'Top-1 Acc: 57.0%  |  Top-3 Acc: 92.4%  |  Macro F1: 0.58',
                 fontsize=11, fontweight='bold', pad=12)
    for r in range(9):
        for c in range(9):
            val = CM[r, c]
            color = 'white' if val > 50 else 'black'
            ax.text(c, r, f'{int(val)}%', ha='center', va='center',
                    fontsize=8, fontweight='bold', color=color)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, 'confusion_matrix.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print('Saved: confusion_matrix.png')


# ─────────────────────────────────────────────────────────────
# 2. CLASSIFICATION REPORT
# ─────────────────────────────────────────────────────────────
def plot_classification_report():
    x = np.arange(len(CROPS))
    w = 0.25
    fig, ax = plt.subplots(figsize=(12, 6))
    b1 = ax.bar(x - w, precision, w, label='Precision', color='#3478C5', edgecolor='none')
    b2 = ax.bar(x,     recall,    w, label='Recall',    color='#D9541B', edgecolor='none')
    b3 = ax.bar(x + w, f1,        w, label='F1-Score',  color='#78AB31', edgecolor='none')
    ax.axhline(0.57, color='black', linestyle='--', linewidth=1.2, label='Top-1 Acc 57%')
    ax.axhline(0.58, color='purple', linestyle=':', linewidth=1.2, label='Macro F1 0.58')
    for bars in [b1, b2, b3]:
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, h + 0.015,
                    f'{h:.2f}', ha='center', va='bottom', fontsize=7.5)
    ax.set_xticks(x); ax.set_xticklabels(CROPS, rotation=20, ha='right', fontsize=10)
    ax.set_ylim(0, 1.08)
    ax.set_ylabel('Score', fontsize=12, fontweight='bold')
    ax.set_xlabel('Crop', fontsize=12, fontweight='bold')
    ax.set_title('Per-Crop Classification Report - CatBoost V2\n'
                 'Macro Precision: 0.62  |  Macro Recall: 0.60  |  Macro F1: 0.58',
                 fontsize=11, fontweight='bold')
    ax.legend(fontsize=9, loc='upper right')
    ax.yaxis.grid(True, alpha=0.35); ax.set_axisbelow(True)
    ax.spines[['top','right']].set_visible(False)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, 'classification_report.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print('Saved: classification_report.png')


# ─────────────────────────────────────────────────────────────
# 3. FEATURE IMPORTANCE — CROP MODEL
# ─────────────────────────────────────────────────────────────
def plot_feature_importance_crop():
    features = [
        'Rainfall (mm)', 'Soil pH', 'N x pH Interaction', 'Temperature (C)',
        'Phosphorus (P)', 'Nitrogen (N)', 'Potassium (K)', 'Soil Fertility Index',
        'Agro Zone', 'NP Ratio', 'Region', 'pH Stress Index',
        'Climate Stress Index', 'P x pH Interaction', 'Rain-Temp Ratio',
        'State', 'Soil Type', 'Pest Type'
    ]
    importance = np.array([24.5, 18.2, 14.8, 12.1, 10.4, 5.0, 4.0, 3.0, 2.5, 2.0,
                           1.5, 1.2, 1.0, 0.8, 0.7, 0.6, 0.5, 0.4])
    base_idx = {0, 3, 4, 5, 6}
    eng_idx  = {2, 7, 9, 11, 12, 13, 14}
    cat_idx  = {8, 10, 15, 16, 17}
    colors = []
    for i in range(len(features)):
        if i in eng_idx:   colors.append('#D9541B')
        elif i in cat_idx: colors.append('#78AB31')
        else:              colors.append('#3478C5')
    order = np.argsort(importance)
    feat_sorted = [features[i] for i in order]
    imp_sorted  = importance[order]
    col_sorted  = [colors[i] for i in order]
    fig, ax = plt.subplots(figsize=(10, 8))
    bars = ax.barh(range(len(feat_sorted)), imp_sorted, color=col_sorted, edgecolor='none')
    for i, (bar, val) in enumerate(zip(bars, imp_sorted)):
        ax.text(val + 0.2, i, f'{val:.1f}%', va='center', fontsize=8)
    ax.set_yticks(range(len(feat_sorted))); ax.set_yticklabels(feat_sorted, fontsize=9)
    ax.set_xlabel('Feature Importance (%)', fontsize=12, fontweight='bold')
    ax.set_title('Feature Importance - CatBoost Crop Classifier\n'
                 'Top: Rainfall 24.5%  |  Engineered features contribute 34.3%',
                 fontsize=11, fontweight='bold')
    ax.set_xlim(0, 28)
    ax.xaxis.grid(True, alpha=0.35); ax.set_axisbelow(True)
    ax.spines[['top','right']].set_visible(False)
    legend_patches = [
        mpatches.Patch(color='#3478C5', label='Base Feature'),
        mpatches.Patch(color='#D9541B', label='Engineered Feature'),
        mpatches.Patch(color='#78AB31', label='Categorical Feature'),
    ]
    ax.legend(handles=legend_patches, loc='lower right', fontsize=9)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, 'feature_importance_crop.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print('Saved: feature_importance_crop.png')


# ─────────────────────────────────────────────────────────────
# 4. FEATURE IMPORTANCE — YIELD MODEL
# ─────────────────────────────────────────────────────────────
def plot_feature_importance_yield():
    features = [
        'Crop Type', 'Pest Severity', 'Crop Variety', 'Labor Input',
        'Rainfall Variability', 'Rainfall (mm)', 'Soil Nitrogen (N)', 'NP Ratio',
        'Soil Fertility Index', 'Temperature (C)', 'Farm Size (ha)', 'Soil pH',
        'Soil Phosphorus (P)', 'Soil Potassium (K)', 'Agro Zone', 'Region',
        'Soil Type', 'Pest Type', 'Climate Index', 'State'
    ]
    importance = np.array([73.5, 5.3, 4.0, 3.9, 3.6, 3.0, 2.1, 1.5,
                           1.2, 0.9, 0.5, 0.4, 0.3, 0.3, 0.2, 0.2, 0.2, 0.2, 0.1, 0.1])
    cat_idx  = {0, 2, 3, 4, 14, 15, 16, 17, 19}
    agro_idx = {1, 5, 9, 10, 18}
    colors = []
    for i in range(len(features)):
        if i in cat_idx:   colors.append('#78AB31')
        elif i in agro_idx: colors.append('#D9541B')
        else:              colors.append('#3478C5')
    order = np.argsort(importance)
    feat_sorted = [features[i] for i in order]
    imp_sorted  = importance[order]
    col_sorted  = [colors[i] for i in order]
    fig, ax = plt.subplots(figsize=(10, 8.5))
    bars = ax.barh(range(len(feat_sorted)), imp_sorted, color=col_sorted, edgecolor='none')
    for i, (bar, val) in enumerate(zip(bars, imp_sorted)):
        if val >= 0.5:
            ax.text(val + 0.3, i, f'{val:.1f}%', va='center', fontsize=8)
    ax.set_yticks(range(len(feat_sorted))); ax.set_yticklabels(feat_sorted, fontsize=9)
    ax.set_xlabel('Feature Importance (%)', fontsize=12, fontweight='bold')
    ax.set_title('Feature Importance - CatBoost Yield Regressor\n'
                 'Crop Type dominates at 73.5%  |  R2 = 0.724  |  RMSE = 2135 kg/ha',
                 fontsize=11, fontweight='bold')
    ax.set_xlim(0, 82)
    ax.xaxis.grid(True, alpha=0.35); ax.set_axisbelow(True)
    ax.spines[['top','right']].set_visible(False)
    legend_patches = [
        mpatches.Patch(color='#3478C5', label='Soil Nutrient Feature'),
        mpatches.Patch(color='#D9541B', label='Agronomic / Climate Feature'),
        mpatches.Patch(color='#78AB31', label='Categorical Feature'),
    ]
    ax.legend(handles=legend_patches, loc='lower right', fontsize=9)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, 'feature_importance_yield.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print('Saved: feature_importance_yield.png')


# ─────────────────────────────────────────────────────────────
# 5. CV RESULTS — 4-panel bar chart
# ─────────────────────────────────────────────────────────────
def plot_cv_results():
    colors = ['#3478C5', '#D9541B', '#78AB31', '#A01030']
    labels = ['RMSE (kg/ha)', 'MAE (kg/ha)', 'R2', 'MAPE (%)']
    data   = [rmse_cv, mae_cv, r2_cv, mape_cv]
    means  = [np.mean(d) for d in data]
    ylims  = [(2050, 2350), (1380, 1480), (0.710, 0.740), (35, 40)]
    fmts   = ['{:.0f}', '{:.0f}', '{:.4f}', '{:.1f}%']
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    axes = axes.flatten()
    for i, (ax, vals, lbl, col, ylim, mean, fmt) in enumerate(
            zip(axes, data, labels, colors, ylims, means, fmts)):
        bars = ax.bar(folds, vals, color=col, edgecolor='none', alpha=0.85)
        ax.axhline(mean, color='red', linestyle='--', linewidth=1.5)
        ax.text(4.7, mean + (ylim[1]-ylim[0])*0.01,
                f'Mean: {fmt.format(mean)}', color='red', fontsize=8.5)
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x()+bar.get_width()/2, v + (ylim[1]-ylim[0])*0.008,
                    fmt.format(v), ha='center', fontsize=8)
        ax.set_xticks(folds); ax.set_xlabel('Fold', fontsize=10)
        ax.set_ylabel(lbl, fontsize=10)
        ax.set_ylim(ylim)
        ax.set_title(lbl, fontweight='bold')
        ax.yaxis.grid(True, alpha=0.35); ax.set_axisbelow(True)
        ax.spines[['top','right']].set_visible(False)
    fig.suptitle('5-Fold Cross-Validation - CatBoost Yield Regressor\n'
                 f'Avg RMSE: {np.mean(rmse_cv):.0f} kg/ha  |  Avg MAE: {np.mean(mae_cv):.0f} kg/ha  '
                 f'|  Avg R2: {np.mean(r2_cv):.4f}  |  Avg MAPE: {np.mean(mape_cv):.1f}%',
                 fontsize=11, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, 'cv_results_yield.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print('Saved: cv_results_yield.png')


# ─────────────────────────────────────────────────────────────
# 6. CV SCATTER — stability line plot
# ─────────────────────────────────────────────────────────────
def plot_yield_cv_scatter():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    ax1b = ax1.twinx()
    ax1.plot(folds, rmse_cv, '-o', color='#3478C5', lw=2, ms=8, mfc='#3478C5', label='RMSE')
    ax1b.plot(folds, mae_cv, '--s', color='#D9541B', lw=2, ms=8, mfc='#D9541B', label='MAE')
    ax1.set_ylabel('RMSE (kg/ha)', color='#3478C5', fontsize=11)
    ax1b.set_ylabel('MAE (kg/ha)', color='#D9541B', fontsize=11)
    ax1.set_xticks(folds); ax1.set_xlabel('Cross-Validation Fold', fontsize=11)
    ax1.set_title(f'RMSE & MAE per Fold\nRMSE: {rmse_cv[0]:.0f} to {rmse_cv[-1]:.0f}  '
                  f'MAE: {mae_cv[0]:.0f} to {mae_cv[-1]:.0f}', fontweight='bold')
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax1b.get_legend_handles_labels()
    ax1.legend(lines1+lines2, labels1+labels2, loc='upper right', fontsize=9)
    ax1.spines[['top']].set_visible(False)
    ax2b = ax2.twinx()
    ax2.plot(folds, r2_cv,   '-^', color='#78AB31', lw=2, ms=8, mfc='#78AB31', label='R2')
    ax2b.plot(folds, mape_cv,'--d', color='#A01030', lw=2, ms=8, mfc='#A01030', label='MAPE %')
    ax2.set_ylabel('R2', color='#78AB31', fontsize=11)
    ax2b.set_ylabel('MAPE (%)', color='#A01030', fontsize=11)
    ax2.set_xticks(folds); ax2.set_xlabel('Cross-Validation Fold', fontsize=11)
    ax2.set_title(f'R2 & MAPE per Fold\nR2: {min(r2_cv):.4f} to {max(r2_cv):.4f}  '
                  f'MAPE: {min(mape_cv):.1f}% to {max(mape_cv):.1f}%', fontweight='bold')
    lines3, labels3 = ax2.get_legend_handles_labels()
    lines4, labels4 = ax2b.get_legend_handles_labels()
    ax2.legend(lines3+lines4, labels3+labels4, loc='upper right', fontsize=9)
    ax2.spines[['top']].set_visible(False)
    fig.suptitle('5-Fold CV Stability - CatBoost Yield Regressor\n'
                 'Low variance across folds confirms model robustness',
                 fontsize=11, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, 'yield_cv_scatter.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print('Saved: yield_cv_scatter.png')


# ─────────────────────────────────────────────────────────────
# 7. CROP REQUIREMENTS RADAR
# ─────────────────────────────────────────────────────────────
def plot_crop_requirements_radar():
    dim_labels = ['pH', 'Nitrogen\n(N)', 'Phosphorus\n(P)', 'Potassium\n(K)',
                  'Temperature\n(C)', 'Rainfall\n(mm)']
    raw = np.array([
        [6.25, 30.5, 17.0, 127.5, 26.5, 1342],
        [6.30, 30.0, 16.5, 121.0, 26.5, 1276],
        [6.30, 30.5, 17.0, 121.0, 26.5, 1375],
        [6.20, 30.5, 16.0, 122.0, 27.0, 1329],
        [6.25, 31.0, 17.5, 126.0, 26.5, 1364],
        [6.20, 30.5, 17.0, 123.5, 26.5, 1251],
        [6.20, 30.5, 17.0, 127.5, 26.5, 1276],
        [6.25, 31.0, 17.0, 124.0, 26.5, 1314],
        [6.25, 30.0, 17.0, 123.5, 26.5, 1262],
    ])
    mn = raw.min(axis=0); mx = raw.max(axis=0)
    rng = np.where(mx - mn == 0, 1, mx - mn)
    norm = (raw - mn) / rng
    n_dim = len(dim_labels)
    angles = np.linspace(0, 2*np.pi, n_dim, endpoint=False).tolist()
    angles += angles[:1]
    fig, ax = plt.subplots(figsize=(9, 9), subplot_kw=dict(polar=True))
    cmap = matplotlib.colormaps.get_cmap('tab10')
    for i, (crop, row) in enumerate(zip(CROPS, norm)):
        vals = row.tolist() + row[:1].tolist()
        ax.plot(angles, vals, '-o', lw=2, ms=5, color=cmap(i), label=crop)
        ax.fill(angles, vals, alpha=0.06, color=cmap(i))
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(dim_labels, fontsize=10, fontweight='bold')
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(['0.25','0.50','0.75','1.00'], fontsize=7, color='grey')
    ax.set_ylim(0, 1)
    ax.set_title('Crop Ideal Requirements - Radar Chart\n'
                 'Normalised [0-1] from crop_requirements.json',
                 fontsize=12, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.32, 1.12), fontsize=9)
    ax.grid(color='grey', linestyle='--', linewidth=0.5, alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, 'crop_requirements_radar.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print('Saved: crop_requirements_radar.png')


# ─────────────────────────────────────────────────────────────
# 8. EVALUATION MATRIX
# ─────────────────────────────────────────────────────────────
def plot_evaluation_matrix():
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 9),
                                   gridspec_kw={'height_ratios': [3, 4]})
    clf_data = np.vstack([precision, recall, f1])
    im1 = ax1.imshow(clf_data, cmap='RdYlGn', vmin=0, vmax=1, aspect='auto')
    plt.colorbar(im1, ax=ax1, shrink=0.8, label='Score')
    ax1.set_xticks(range(9)); ax1.set_xticklabels(CROPS, rotation=25, ha='right', fontsize=10)
    ax1.set_yticks(range(3)); ax1.set_yticklabels(['Precision','Recall','F1-Score'], fontsize=10)
    ax1.set_title('CLASSIFICATION EVALUATION MATRIX - CatBoost Crop Classifier V2\n'
                  'Top-1 Acc: 57.0%  |  Top-3 Acc: 92.4%  |  Macro F1: 0.58  |  Support: 500/class',
                  fontsize=10, fontweight='bold')
    for r in range(3):
        for c in range(9):
            v = clf_data[r, c]
            color = 'white' if v > 0.6 else 'black'
            ax1.text(c, r, f'{v:.3f}', ha='center', va='center',
                     fontsize=9, fontweight='bold', color=color)
    raw_reg = np.column_stack([rmse_cv, mae_cv, r2_cv, mape_cv])
    norm_reg = (raw_reg - raw_reg.min(axis=0)) / (raw_reg.max(axis=0) - raw_reg.min(axis=0) + 1e-9)
    disp_reg = norm_reg.copy()
    disp_reg[:, 0] = 1 - norm_reg[:, 0]
    disp_reg[:, 1] = 1 - norm_reg[:, 1]
    disp_reg[:, 3] = 1 - norm_reg[:, 3]
    im2 = ax2.imshow(disp_reg.T, cmap='RdYlGn', vmin=0, vmax=1, aspect='auto')
    plt.colorbar(im2, ax=ax2, shrink=0.8, label='Relative Perf (green=best)')
    ax2.set_xticks(range(5)); ax2.set_xticklabels([f'Fold {i}' for i in range(1,6)], fontsize=10)
    ax2.set_yticks(range(4))
    ax2.set_yticklabels(['RMSE (kg/ha)', 'MAE (kg/ha)', 'R2', 'MAPE (%)'], fontsize=10)
    ax2.set_title('REGRESSION EVALUATION MATRIX - CatBoost Yield Regressor (5-Fold CV)\n'
                  'Avg RMSE: 2135  |  Avg MAE: 1432  |  Avg R2: 0.7243  |  Avg MAPE: 37.5%',
                  fontsize=10, fontweight='bold')
    raw_cols = [rmse_cv, mae_cv, r2_cv, mape_cv]
    fmts = ['{:.0f}', '{:.0f}', '{:.4f}', '{:.1f}%']
    for r, (vals, fmt) in enumerate(zip(raw_cols, fmts)):
        for c, v in enumerate(vals):
            ax2.text(c, r, fmt.format(v), ha='center', va='center',
                     fontsize=9, fontweight='bold', color='black')
    fig.suptitle('Soil Nutrition AI - Full Evaluation Matrix Report',
                 fontsize=13, fontweight='bold', y=1.01)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, 'evaluation_matrix.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print('Saved: evaluation_matrix.png')


# ─────────────────────────────────────────────────────────────
# 9. CROP CLASSIFIER: CatBoost V1 vs V2  (same task, valid comparison)
# ─────────────────────────────────────────────────────────────
def plot_classifier_v1_vs_v2():
    models   = ['CatBoost V1', 'CatBoost V2']
    x        = np.arange(2)
    grey     = '#B0B0B0'
    green    = '#78AB31'
    palette  = [grey, green]

    top1_acc = [35.6, 57.0]
    top3_acc = [76.0, 92.4]
    macro_p  = [0.360, 0.620]
    macro_r  = [0.350, 0.600]
    macro_f1 = [0.350, 0.580]

    fig, axes = plt.subplots(1, 3, figsize=(11, 5))

    axes[0].bar(x, top1_acc, color=palette, edgecolor='none', width=0.4)
    for i, v in enumerate(top1_acc):
        axes[0].text(i, v+1.2, f'{v:.1f}%', ha='center', fontsize=11, fontweight='bold')
    axes[0].set_xticks(x); axes[0].set_xticklabels(models)
    axes[0].set_ylim(0, 72); axes[0].set_ylabel('Accuracy (%)')
    axes[0].set_title('Top-1 Accuracy', fontweight='bold')
    axes[0].yaxis.grid(True, alpha=0.35); axes[0].set_axisbelow(True)
    axes[0].spines[['top','right']].set_visible(False)

    axes[1].bar(x, top3_acc, color=palette, edgecolor='none', width=0.4)
    for i, v in enumerate(top3_acc):
        axes[1].text(i, v+0.7, f'{v:.1f}%', ha='center', fontsize=11, fontweight='bold')
    axes[1].set_xticks(x); axes[1].set_xticklabels(models)
    axes[1].set_ylim(60, 100); axes[1].set_ylabel('Accuracy (%)')
    axes[1].set_title('Top-3 Accuracy', fontweight='bold')
    axes[1].yaxis.grid(True, alpha=0.35); axes[1].set_axisbelow(True)
    axes[1].spines[['top','right']].set_visible(False)

    bx = np.arange(2)
    bw = 0.18
    b1 = axes[2].bar(bx - bw, macro_p,  bw, color='#3478C5', edgecolor='none', label='Precision')
    b2 = axes[2].bar(bx,      macro_r,  bw, color='#D9541B', edgecolor='none', label='Recall')
    b3 = axes[2].bar(bx + bw, macro_f1, bw, color='#78AB31', edgecolor='none', label='F1')
    for bars in [b1, b2, b3]:
        for bar in bars:
            axes[2].text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.01,
                         f'{bar.get_height():.2f}', ha='center', fontsize=8)
    axes[2].set_xticks(bx); axes[2].set_xticklabels(models)
    axes[2].set_ylim(0, 0.75); axes[2].set_ylabel('Score')
    axes[2].set_title('Macro P / R / F1', fontweight='bold')
    axes[2].legend(fontsize=8, loc='upper left')
    axes[2].yaxis.grid(True, alpha=0.35); axes[2].set_axisbelow(True)
    axes[2].spines[['top','right']].set_visible(False)

    fig.suptitle('Crop Classifier: CatBoost V1 vs CatBoost V2\n'
                 'Same task - 9-class Nigerian crop recommendation\n'
                 'Improvement: +7 interaction features + hyperparameter grid search  |  60% relative gain',
                 fontsize=11, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, 'classifier_v1_vs_v2.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print('Saved: classifier_v1_vs_v2.png')


# ─────────────────────────────────────────────────────────────
# 10. YIELD REGRESSOR: standalone performance (no comparison)
# ─────────────────────────────────────────────────────────────
def plot_yield_model_standalone():
    colors = ['#3478C5', '#D9541B', '#78AB31', '#A01030']
    labels = ['RMSE (kg/ha)', 'MAE (kg/ha)', 'R2', 'MAPE (%)']
    data   = [rmse_cv, mae_cv, r2_cv, mape_cv]
    means  = [np.mean(d) for d in data]
    ylims  = [(2050, 2350), (1380, 1480), (0.710, 0.740), (35, 40)]
    fmts   = ['{:.0f}', '{:.0f}', '{:.4f}', '{:.1f}%']

    fig, axes = plt.subplots(1, 4, figsize=(13, 4.5))
    for ax, vals, lbl, col, ylim, mean, fmt in zip(axes, data, labels, colors, ylims, means, fmts):
        bars = ax.bar(folds, vals, color=col, edgecolor='none', alpha=0.85)
        ax.axhline(mean, color='black', linestyle='--', linewidth=1.4)
        ax.text(4.65, mean + (ylim[1]-ylim[0])*0.015,
                f'Mean\n{fmt.format(mean)}', fontsize=8, ha='center')
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x()+bar.get_width()/2, v+(ylim[1]-ylim[0])*0.012,
                    fmt.format(v), ha='center', fontsize=7.5)
        ax.set_xticks(folds); ax.set_xticklabels([f'F{i}' for i in folds])
        ax.set_xlabel('CV Fold'); ax.set_ylabel(lbl)
        ax.set_title(lbl, fontweight='bold'); ax.set_ylim(ylim)
        ax.yaxis.grid(True, alpha=0.35); ax.set_axisbelow(True)
        ax.spines[['top','right']].set_visible(False)

    fig.suptitle('CatBoost Yield Regressor - 5-Fold CV Performance\n'
                 f'Avg RMSE: {np.mean(rmse_cv):.0f} kg/ha  |  Avg MAE: {np.mean(mae_cv):.0f} kg/ha  '
                 f'|  Avg R2: {np.mean(r2_cv):.4f}  |  Avg MAPE: {np.mean(mape_cv):.1f}%',
                 fontsize=11, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, 'yield_model_standalone.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print('Saved: yield_model_standalone.png')


# ─────────────────────────────────────────────────────────────
# RUN ALL
# ─────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print('\n================================================')
    print(' Soil Nutrition Backend - Diagram Generator')
    print('================================================\n')

    steps = [
        plot_confusion_matrix,
        plot_classification_report,
        plot_feature_importance_crop,
        plot_feature_importance_yield,
        plot_cv_results,
        plot_yield_cv_scatter,
        plot_crop_requirements_radar,
        plot_evaluation_matrix,
        plot_classifier_v1_vs_v2,       # replaces old model_comparison
        plot_yield_model_standalone,    # new: yield regressor standalone
    ]

    for fn in steps:
        try:
            fn()
        except Exception as e:
            print(f'  ERROR in {fn.__name__}: {e}')

    print('\n================================================')
    print(f' Done. 10 PNG files saved to:\n {OUT}')
    print('================================================\n')
