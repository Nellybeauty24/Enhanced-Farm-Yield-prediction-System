% =========================================================================
% SCRIPT 1: script_1_crop_classification_metrics.m
% Crop Recommendation Model — Per-Class & Overall Classification Metrics
% -------------------------------------------------------------------------
% Model  : CatBoost Multiclass Classifier V2.1.0
% Classes: 9 (Beans, Cassava, Maize, Onions, Pepper, Rice, Sorghum, Tomato, Yam)
% Dataset: Nigeria Agricultural Multi-Environmental Dataset (20,000 records)
% Source : ACADEMIC_MODEL_REPORT_V2.md | CROP_MODEL_PERFORMANCE_REPORT.md
% =========================================================================
clear; clc; close all;

%% ---- DATA ---------------------------------------------------------------

% Per-class metrics (4 of 9 classes individually documented in reports)
crops_4      = {'Cassava', 'Maize', 'Rice', 'Tomato'};
precision_4  = [0.57, 0.73, 0.73, 0.45];
recall_4     = [0.78, 0.20, 0.34, 0.80];
f1_4         = [0.66, 0.31, 0.46, 0.57];

% Overall performance metrics
overall_labels = {'Random Baseline (1/9 = 11.1%)', ...
                  'Macro F1-Score',                ...
                  'Weighted Precision',            ...
                  'Top-1 Accuracy (Global)',       ...
                  'Top-3 Accuracy (Consultative)'};
overall_vals   = [11.1, 58.0, 61.0, 57.0, 92.4];

%% ---- FIGURE 1: Grouped Bar — Per-Class Precision / Recall / F1 ----------
fig1 = figure('Name', 'Fig1 Per-Class Metrics', 'NumberTitle', 'off', ...
              'Position', [60, 60, 940, 560]);

data_mat = [precision_4; recall_4; f1_4]';   % 4x3  (rows=crops, cols=metrics)
b = bar(data_mat, 'grouped');
b(1).FaceColor = [0.20, 0.52, 0.90];   % blue   — Precision
b(2).FaceColor = [0.95, 0.40, 0.15];   % orange — Recall
b(3).FaceColor = [0.15, 0.72, 0.35];   % green  — F1

set(gca, 'XTickLabel', crops_4, 'FontSize', 12, ...
         'TickLabelInterpreter', 'none');
ylim([0, 1.08]);
yticks(0 : 0.1 : 1.0);
ylabel('Score', 'FontSize', 13);
title({'CatBoost Crop Classifier V2.1.0 — Per-Class Performance', ...
       '(4 of 9 classes documented; Macro F1 = 0.58 over all 9 classes)'}, ...
      'FontSize', 12, 'FontWeight', 'bold');
legend({'Precision', 'Recall', 'F1-Score'}, 'Location', 'northeast', 'FontSize', 11);
grid on; box on;

% Annotate each bar
nGroups = 4;
nSeries = 3;
all_vals = {precision_4, recall_4, f1_4};
for j = 1 : nSeries
    for i = 1 : nGroups
        text(b(j).XEndPoints(i), b(j).YEndPoints(i) + 0.024, ...
             sprintf('%.2f', all_vals{j}(i)), ...
             'HorizontalAlignment', 'center', 'FontSize', 9, 'FontWeight', 'bold');
    end
end

print(fig1, 'fig1_crop_per_class_metrics', '-dpng', '-r300');
fprintf('Saved: fig1_crop_per_class_metrics.png\n');

%% ---- FIGURE 2: Overall Accuracy — All 5 KPIs ----------------------------
fig2 = figure('Name', 'Fig2 Overall Accuracy', 'NumberTitle', 'off', ...
              'Position', [60, 60, 940, 540]);

bar_colors = [0.80, 0.20, 0.20;   % red    — baseline
              0.55, 0.35, 0.80;   % purple — macro f1
              0.20, 0.52, 0.90;   % blue   — weighted prec
              0.20, 0.52, 0.90;   % blue   — top-1
              0.15, 0.72, 0.35];  % green  — top-3

b2 = bar(overall_vals, 'FaceColor', 'flat');
for i = 1 : 5
    b2.CData(i, :) = bar_colors(i, :);
end

set(gca, 'XTickLabel', overall_labels, 'FontSize', 10, ...
         'TickLabelInterpreter', 'none');
xtickangle(12);
ylim([0, 105]);
ylabel('Score / Accuracy (%)', 'FontSize', 13);
title({'CatBoost Crop Classifier V2.1.0 — Overall KPI Dashboard', ...
       '5× improvement over random baseline; 92.4% Top-3 accuracy'}, ...
      'FontSize', 12, 'FontWeight', 'bold');
grid on; box on;
yline(100, '--k', 'LineWidth', 1.2);

for i = 1 : 5
    text(i, overall_vals(i) + 1.8, sprintf('%.1f%%', overall_vals(i)), ...
         'HorizontalAlignment', 'center', 'FontSize', 11, 'FontWeight', 'bold');
end

print(fig2, 'fig2_overall_accuracy', '-dpng', '-r300');
fprintf('Saved: fig2_overall_accuracy.png\n');

%% ---- EVALUATION MATRIX (Console Output) ---------------------------------
fprintf('\n============================================================\n');
fprintf('  CROP CLASSIFICATION — EVALUATION MATRIX (Per-Class)\n');
fprintf('============================================================\n');
fprintf('%-10s  %-10s  %-10s  %-10s\n', 'Crop', 'Precision', 'Recall', 'F1-Score');
fprintf('%s\n', repmat('-', 1, 48));
for i = 1 : 4
    fprintf('%-10s  %-10.2f  %-10.2f  %-10.2f\n', ...
            crops_4{i}, precision_4(i), recall_4(i), f1_4(i));
end
fprintf('%s\n', repmat('-', 1, 48));
fprintf('%-10s  %-10s  %-10s  %-10.2f\n', 'Macro Avg', '  —', '  —', mean(f1_4));
fprintf('\n  Global Accuracy (Top-1) : 57.0%%  [95%% CI: ±1.2%%]\n');
fprintf('  Top-3 Accuracy          : 92.4%%  [95%% CI: ±0.8%%]\n');
fprintf('  Macro F1-Score          : 58.0%%\n');
fprintf('  Weighted Precision      : 61.0%%\n');
fprintf('  Random Baseline (1/9)   : 11.1%%\n');
fprintf('  Improvement over Random : 5.1× (Top-1)\n');
fprintf('============================================================\n\n');
