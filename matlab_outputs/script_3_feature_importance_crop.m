% =========================================================================
% SCRIPT 3: script_3_feature_importance_crop.m
% Crop Recommendation Model — Top-5 Feature Importance
% -------------------------------------------------------------------------
% Model  : CatBoost Multiclass Classifier V2.1.0
% Source : CROP_MODEL_PERFORMANCE_REPORT.md / ACADEMIC_MODEL_REPORT_V2.md
% Note   : These top-5 values are for the CROP classifier (22 input features).
%          The yield model's feature importance is in script_4.
% =========================================================================
clear; clc; close all;

%% ---- DATA ---------------------------------------------------------------
% Top-5 feature importance for the Crop Recommendation CatBoost classifier
% (from CROP_MODEL_PERFORMANCE_REPORT.md, Section: Feature Importance)
features = { ...
    'Rainfall (mm)',              ...   % rank 1
    'Soil pH',                    ...   % rank 2
    'N x pH Interaction',         ...   % rank 3  (engineered: N * pH)
    'Temperature (C)',            ...   % rank 4
    'Soil Phosphorus (P)'         };    % rank 5

importance = [24.5, 18.2, 14.8, 12.1, 10.4];

% Engineering flags (1 = domain-engineered feature, 0 = raw sensor)
is_engineered = [0, 0, 1, 0, 0];

%% ---- FIGURE 5: Horizontal Bar — Feature Importance ----------------------
fig5 = figure('Name', 'Fig5 Crop Feature Importance', 'NumberTitle', 'off', ...
              'Position', [80, 80, 870, 480]);

bar_colors = [0.20, 0.52, 0.90;   % blue   — Rainfall
              0.15, 0.72, 0.35;   % green  — Soil pH
              0.90, 0.30, 0.20;   % red    — Engineered interaction
              0.95, 0.62, 0.10;   % amber  — Temperature
              0.55, 0.25, 0.78];  % purple — Phosphorus

b5 = barh(importance, 'FaceColor', 'flat');
for i = 1:5
    b5.CData(i,:) = bar_colors(i,:);
end

set(gca, 'YTickLabel', features, 'FontSize', 12, ...
         'TickLabelInterpreter', 'none');
xlabel('Feature Importance (%)', 'FontSize', 13);
title({'Crop Recommendation Model (CatBoost V2.1.0)', ...
       'Top-5 Feature Importance — Soil, Climate & Engineered Interactions'}, ...
      'FontSize', 12, 'FontWeight', 'bold');
xlim([0, 31]);
grid on; box on;

for i = 1:5
    lbl = sprintf('%.1f%%', importance(i));
    if is_engineered(i)
        lbl = [lbl, '  [engineered]'];
    end
    text(importance(i) + 0.5, i, lbl, ...
         'VerticalAlignment', 'middle', 'FontSize', 10, 'FontWeight', 'bold');
end

% Cumulative importance annotation
cum_pct = sum(importance);
dim_ann = [0.62, 0.04, 0.30, 0.07];
annotation('textbox', dim_ann, ...
           'String', sprintf('Top-5 cumulative importance: %.1f%%', cum_pct), ...
           'FontSize', 9, 'EdgeColor', [0.5 0.5 0.5], ...
           'BackgroundColor', [0.96 0.96 0.96], 'FitBoxToText', 'on');

print(fig5, 'fig5_feature_importance_crop', '-dpng', '-r300');
fprintf('Saved: fig5_feature_importance_crop.png\n');

%% ---- FEATURE IMPORTANCE MATRIX (Console) --------------------------------
fprintf('\n=======================================================\n');
fprintf('  CROP MODEL — FEATURE IMPORTANCE RANKING (Top 5/22)\n');
fprintf('=======================================================\n');
fprintf('%-5s  %-30s  %-12s  %-10s\n', 'Rank', 'Feature', 'Importance', 'Type');
fprintf('%s\n', repmat('-', 1, 62));
types = {'Raw', 'Raw', 'Engineered', 'Raw', 'Raw'};
for i = 1:5
    fprintf('%-5d  %-30s  %-12.1f  %-10s\n', i, features{i}, importance(i), types{i});
end
fprintf('%s\n', repmat('-', 1, 62));
fprintf('  Cumulative Top-5 importance: %.1f%%\n', sum(importance));
fprintf('  Total features in model: 22 (8 categorical + 14 numeric)\n');
fprintf('=======================================================\n\n');
