% =========================================================================
% SCRIPT 4: script_4_feature_importance_yield.m
% Yield Prediction Model — Full Feature Importance (All 20 Features)
% -------------------------------------------------------------------------
% Model  : CatBoost Regressor
% Target : yield_kg_ha (kg per hectare)
% Source : outputs/feature_importance.csv (exact values preserved)
% =========================================================================
clear; clc; close all;

%% ---- DATA (from outputs/feature_importance.csv — exact values) ----------
features_raw = { ...
    'crop_type',           'pest_severity',       'crop_variety',    ...
    'labor_input',         'rainfall_variability', 'soil_type',      ...
    'climate_index',       'rainfall_mm',          'soil_nitrogen',  ...
    'agro_zone',           'farm_size_ha',         'state',          ...
    'temperature_C',       'np_ratio',             'region',         ...
    'soil_pH',             'soil_fertility_index', 'soil_phosphorus',...
    'pest_type',           'soil_potassium'        };

importance_raw = [ ...
    73.524948, 5.296770, 3.954299, 3.885859, 3.556791, 2.904083, ...
     0.858118, 0.843638, 0.671196, 0.659629, 0.565251, 0.530436, ...
     0.451967, 0.409465, 0.396393, 0.344441, 0.330422, 0.296430, ...
     0.264031, 0.255832 ];

% Sort ascending for horizontal bar chart
[imp_sorted, idx] = sort(importance_raw, 'ascend');
feat_sorted = features_raw(idx);

%% ---- FIGURE 6: Full Feature Importance — All 20 -------------------------
fig6 = figure('Name', 'Fig6 Yield Feature Importance', 'NumberTitle', 'off', ...
              'Position', [40, 40, 960, 760]);

cmap = parula(length(imp_sorted));
b6 = barh(imp_sorted, 'FaceColor', 'flat');
for i = 1:length(imp_sorted)
    b6.CData(i,:) = cmap(i,:);
end

set(gca, 'YTickLabel', feat_sorted, 'FontSize', 9.5, ...
         'TickLabelInterpreter', 'none');
xlabel('Feature Importance (%)', 'FontSize', 13);
title({'Yield Prediction Model (CatBoost Regressor)', ...
       'Full Feature Importance Ranking — All 20 Input Features'}, ...
      'FontSize', 12, 'FontWeight', 'bold');
grid on; box on;

% Annotate bars > 0.8%
for i = 1:length(imp_sorted)
    if imp_sorted(i) >= 0.8
        text(imp_sorted(i) + 0.6, i, sprintf('%.2f%%', imp_sorted(i)), ...
             'VerticalAlignment', 'middle', 'FontSize', 9, 'FontWeight', 'bold');
    end
end

print(fig6, 'fig6_feature_importance_yield_all', '-dpng', '-r300');
fprintf('Saved: fig6_feature_importance_yield_all.png\n');

%% ---- FIGURE 7: Zoomed — Top 6 Non-Dominant Features --------------------
% crop_type dominates (73.5%). This plot shows the remaining features at scale.
top5_idx  = (length(imp_sorted) - 5) : length(imp_sorted);  % top 6 (excl. crop_type)
% Actually let's show all except crop_type (which is at rank 20 after ascend sort)
non_dom_imp  = imp_sorted(1:end-1);          % all except crop_type (the last after sort)
non_dom_feat = feat_sorted(1:end-1);

fig7 = figure('Name', 'Fig7 Yield FI Zoomed', 'NumberTitle', 'off', ...
              'Position', [80, 80, 960, 720]);

cmap2 = hot(length(non_dom_imp));
b7 = barh(non_dom_imp, 'FaceColor', 'flat');
for i = 1:length(non_dom_imp)
    b7.CData(i,:) = cmap2(i,:);
end

set(gca, 'YTickLabel', non_dom_feat, 'FontSize', 10, ...
         'TickLabelInterpreter', 'none');
xlabel('Feature Importance (%)', 'FontSize', 13);
title({'Yield Prediction Model — Feature Importance (Excluding crop\_type)', ...
       'crop\_type excluded (73.5%); shows relative influence of other predictors'}, ...
      'FontSize', 12, 'FontWeight', 'bold', 'Interpreter', 'none');
grid on; box on;

for i = 1:length(non_dom_imp)
    text(non_dom_imp(i) + 0.05, i, sprintf('%.3f%%', non_dom_imp(i)), ...
         'VerticalAlignment', 'middle', 'FontSize', 9);
end

print(fig7, 'fig7_feature_importance_yield_zoomed', '-dpng', '-r300');
fprintf('Saved: fig7_feature_importance_yield_zoomed.png\n');

%% ---- FEATURE IMPORTANCE MATRIX (Console) --------------------------------
fprintf('\n============================================================\n');
fprintf('  YIELD MODEL — FEATURE IMPORTANCE MATRIX (All 20 Features)\n');
fprintf('============================================================\n');
fprintf('%-5s  %-25s  %-14s  %-14s\n', 'Rank', 'Feature', 'Importance%%', 'Cumulative%%');
fprintf('%s\n', repmat('-', 1, 62));
[imp_desc, idx_desc] = sort(importance_raw, 'descend');
feat_desc = features_raw(idx_desc);
cumulative = 0;
for i = 1:20
    cumulative = cumulative + imp_desc(i);
    fprintf('%-5d  %-25s  %-14.6f  %-14.4f\n', i, feat_desc{i}, imp_desc(i), cumulative);
end
fprintf('============================================================\n');
fprintf('  crop_type alone accounts for %.2f%% of importance\n', imp_desc(1));
fprintf('  Top-5 features account for   %.2f%%\n', sum(imp_desc(1:5)));
fprintf('  Top-10 features account for  %.2f%%\n', sum(imp_desc(1:10)));
fprintf('============================================================\n\n');
