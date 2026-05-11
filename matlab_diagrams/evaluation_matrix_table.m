% =========================================================
% Evaluation Matrix — Full Report (Classification + Regression)
% Exports one combined figure with both tables rendered as heat-maps
% =========================================================

% ---- TABLE 1: Crop Classification Per-Class Report ----
crops = {'Rice','Maize','Cassava','Tomato','Yam','Beans','Sorghum','Pepper','Onions'};
precision = [0.73, 0.73, 0.57, 0.45, 0.58, 0.60, 0.62, 0.65, 0.68];
recall    = [0.34, 0.20, 0.78, 0.80, 0.70, 0.68, 0.72, 0.70, 0.62];
f1        = 2 .* precision .* recall ./ (precision + recall);
support   = repmat(500, 1, 9);

% ---- TABLE 2: Yield Regression CV Summary ----
folds = (1:5)';
rmse_vals = [2222.554; 2161.428; 2146.144; 2130.197; 2114.553];
mae_vals  = [1449.614; 1433.519; 1431.977; 1416.889; 1426.554];
r2_vals   = [0.7242;   0.7180;   0.7262;   0.7182;   0.7303];
mape_vals = [36.68;    37.68;    36.17;    36.91;    38.21];

fig = figure('Name','Evaluation Matrix','Position',[50 50 1100 820]);

% ================================================================
% TOP: Classification heatmap table
% ================================================================
ax1 = subplot(2,1,1);

clf_data = [precision; recall; f1];  % 3 x 9
imagesc(ax1, clf_data);
colormap(ax1, parula);
clim(ax1, [0 1]);
cb1 = colorbar(ax1);
cb1.Label.String = 'Score';

set(ax1, 'XTick', 1:9, 'XTickLabel', crops, 'XTickLabelRotation', 20, ...
         'YTick', 1:3, 'YTickLabel', {'Precision','Recall','F1-Score'}, ...
         'FontSize', 10);
title(ax1, {'CLASSIFICATION EVALUATION MATRIX — CatBoost Crop Classifier V2';
            'Top-1 Accuracy: 57.0%  |  Top-3 Accuracy: 92.4%  |  Macro F1: 0.58  |  Support: 500/class'}, ...
           'FontSize', 11, 'FontWeight', 'bold');

% Overlay values
for r = 1:3
    for c = 1:9
        val = clf_data(r,c);
        text(ax1, c, r, sprintf('%.3f', val), ...
            'HorizontalAlignment','center','VerticalAlignment','middle', ...
            'FontSize', 9, 'FontWeight', 'bold', ...
            'Color', ternary_color(val, 0.55));
    end
end

% ================================================================
% BOTTOM: Regression CV heatmap table
% ================================================================
ax2 = subplot(2,1,2);

% Normalise each metric column for colour mapping
reg_raw  = [rmse_vals, mae_vals, r2_vals, mape_vals];
reg_norm = (reg_raw - min(reg_raw)) ./ (max(reg_raw) - min(reg_raw) + eps);
% Invert RMSE and MAE (lower = better) and MAPE; keep R² as-is
reg_disp = reg_norm;
reg_disp(:,1) = 1 - reg_norm(:,1);  % RMSE: lower is better
reg_disp(:,2) = 1 - reg_norm(:,2);  % MAE:  lower is better
reg_disp(:,4) = 1 - reg_norm(:,4);  % MAPE: lower is better

imagesc(ax2, reg_disp');
colormap(ax2, parula);
clim(ax2, [0 1]);
cb2 = colorbar(ax2);
cb2.Label.String = 'Relative Performance (green=good)';

set(ax2, 'XTick', 1:5, 'XTickLabel', {'Fold 1','Fold 2','Fold 3','Fold 4','Fold 5'}, ...
         'YTick', 1:4, 'YTickLabel', {'RMSE (kg/ha)','MAE (kg/ha)','R²','MAPE (%)'}, ...
         'FontSize', 10);
title(ax2, {'REGRESSION EVALUATION MATRIX — CatBoost Yield Regressor (5-Fold CV)';
            sprintf('Avg RMSE: 2135  |  Avg MAE: 1432  |  Avg R²: 0.7243  |  Avg MAPE: 37.5%%')}, ...
           'FontSize', 11, 'FontWeight', 'bold');

% Overlay raw values
raw_labels = {rmse_vals, mae_vals, r2_vals, mape_vals};
formats    = {'%.0f', '%.0f', '%.4f', '%.1f%%'};
for row = 1:4
    vals = raw_labels{row};
    for col = 1:5
        text(ax2, col, row, sprintf(formats{row}, vals(col)), ...
            'HorizontalAlignment','center','VerticalAlignment','middle', ...
            'FontSize', 9, 'FontWeight', 'bold', 'Color', 'k');
    end
end

sgtitle('Soil Nutrition AI — Full Evaluation Matrix Report', ...
        'FontSize', 13, 'FontWeight', 'bold');

saveas(fig, 'evaluation_matrix.png');
fprintf('Saved: evaluation_matrix.png\n');


% ---- Helper: pick black or white text based on cell brightness ----
function c = ternary_color(val, threshold)
    if val > threshold
        c = 'white';
    else
        c = 'black';
    end
end
