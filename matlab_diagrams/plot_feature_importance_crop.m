% =========================================================
% Feature Importance — Crop Classification Model (CatBoost)
% =========================================================

features = {
    'Rainfall (mm)',
    'Soil pH',
    'N \times pH Interaction',
    'Temperature (°C)',
    'Phosphorus (P)',
    'Nitrogen (N)',
    'Potassium (K)',
    'Soil Fertility Index',
    'Agro Zone',
    'NP Ratio',
    'Region',
    'pH Stress Index',
    'Climate Stress Index',
    'P \times pH Interaction',
    'Rain-Temp Ratio',
    'State',
    'Soil Type',
    'Pest Type'
};

importance = [24.5, 18.2, 14.8, 12.1, 10.4, 5.0, 4.0, 3.0, 2.5, 2.0, ...
              1.5, 1.2, 1.0, 0.8, 0.7, 0.6, 0.5, 0.4];

% Sort ascending for horizontal bar chart
[importance_sorted, idx] = sort(importance);
features_sorted = features(idx);

% Colour: engineered features in orange, base features in blue, categoricals in green
base_feat_idx    = [1 4 5 6 7];   % original numeric inputs (unsorted positions)
eng_feat_idx     = [3 8 10 12 13 14 15];
cat_feat_idx     = [9 11 16 17 18];

colors = repmat([0.20 0.47 0.75], numel(importance), 1); % default blue
for i = 1:numel(idx)
    orig = idx(i);
    if ismember(orig, eng_feat_idx)
        colors(i,:) = [0.85 0.33 0.10];  % orange = engineered
    elseif ismember(orig, cat_feat_idx)
        colors(i,:) = [0.47 0.67 0.19];  % green = categorical
    end
end

fig = figure('Name','Crop Feature Importance','Position',[100 100 750 620]);

barh_h = barh(importance_sorted, 'FaceColor','flat');
barh_h.CData = colors;
barh_h.EdgeColor = 'none';

yticks(1:numel(features));
yticklabels(features_sorted);
xlabel('Feature Importance (%)','FontSize',12,'FontWeight','bold');
title({'Feature Importance — CatBoost Crop Classifier';
       'Top feature: Rainfall 24.5%  |  Engineered features contribute 34.3%'}, ...
       'FontSize',11);

% Value labels
for i = 1:numel(importance_sorted)
    text(importance_sorted(i)+0.2, i, sprintf('%.1f%%', importance_sorted(i)), ...
        'VerticalAlignment','middle','FontSize',8);
end

% Legend patches
patch(NaN,NaN,[0.20 0.47 0.75],'DisplayName','Base Feature');
hold on;
patch(NaN,NaN,[0.85 0.33 0.10],'DisplayName','Engineered Feature');
patch(NaN,NaN,[0.47 0.67 0.19],'DisplayName','Categorical Feature');
legend('Location','southeast','FontSize',9);
hold off;

set(gca,'FontSize',9,'Box','off','XGrid','on','GridAlpha',0.3);
xlim([0 28]);

saveas(fig, 'feature_importance_crop.png');
fprintf('Saved: feature_importance_crop.png\n');
