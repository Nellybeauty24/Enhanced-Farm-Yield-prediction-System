% =========================================================
% Feature Importance — Yield Prediction Model (CatBoost Regressor)
% =========================================================

features = {
    'Crop Type',
    'Pest Severity',
    'Crop Variety',
    'Labor Input',
    'Rainfall Variability',
    'Rainfall (mm)',
    'Soil Nitrogen (N)',
    'NP Ratio',
    'Soil Fertility Index',
    'Temperature (°C)',
    'Farm Size (ha)',
    'Soil pH',
    'Soil Phosphorus (P)',
    'Soil Potassium (K)',
    'Agro Zone',
    'Region',
    'Soil Type',
    'Pest Type',
    'Climate Index',
    'State'
};

importance = [73.5, 5.3, 4.0, 3.9, 3.6, 3.0, 2.1, 1.5, 1.2, 0.9, ...
              0.5, 0.4, 0.3, 0.3, 0.2, 0.2, 0.2, 0.2, 0.1, 0.1];

[imp_sorted, idx] = sort(importance);
feat_sorted = features(idx);

% Colour mapping: categorical = green, numeric soil = blue, agronomic = orange
categorical_pos = [1 3 4 5 15 16 17 18 20];
soil_pos        = [7 8 9 12 13 14];
agronomic_pos   = [2 6 10 11 19];

colors = repmat([0.20 0.47 0.75], numel(importance), 1);
for i = 1:numel(idx)
    orig = idx(i);
    if ismember(orig, categorical_pos)
        colors(i,:) = [0.47 0.67 0.19];
    elseif ismember(orig, agronomic_pos)
        colors(i,:) = [0.85 0.33 0.10];
    end
end

fig = figure('Name','Yield Feature Importance','Position',[100 100 780 680]);

barh_h = barh(imp_sorted, 'FaceColor','flat');
barh_h.CData = colors;
barh_h.EdgeColor = 'none';

yticks(1:numel(feat_sorted));
yticklabels(feat_sorted);
xlabel('Feature Importance (%)','FontSize',12,'FontWeight','bold');
title({'Feature Importance — CatBoost Yield Regressor';
       'Crop Type dominates at 73.5%  |  R² = 0.724  |  RMSE = 2135 kg/ha'}, ...
       'FontSize',11);

for i = 1:numel(imp_sorted)
    if imp_sorted(i) >= 0.5
        text(imp_sorted(i)+0.3, i, sprintf('%.1f%%', imp_sorted(i)), ...
            'VerticalAlignment','middle','FontSize',8);
    end
end

patch(NaN,NaN,[0.20 0.47 0.75],'DisplayName','Soil Nutrient Feature');
hold on;
patch(NaN,NaN,[0.85 0.33 0.10],'DisplayName','Agronomic / Climate Feature');
patch(NaN,NaN,[0.47 0.67 0.19],'DisplayName','Categorical Feature');
legend('Location','southeast','FontSize',9);
hold off;

set(gca,'FontSize',9,'Box','off','XGrid','on','GridAlpha',0.3);
xlim([0 82]);

saveas(fig, 'feature_importance_yield.png');
fprintf('Saved: feature_importance_yield.png\n');
