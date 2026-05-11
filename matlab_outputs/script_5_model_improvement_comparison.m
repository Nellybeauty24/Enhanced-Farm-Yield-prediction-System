% =========================================================================
% SCRIPT 5: script_5_model_improvement_comparison.m
% Crop Classifier — Baseline vs. Optimized V2 Performance Comparison
% -------------------------------------------------------------------------
% Source : CROP_MODEL_PERFORMANCE_REPORT.md (Table: Key Performance Indicators)
% Optimization: Bayesian hyperparameter search + Feature Interaction Engineering
% =========================================================================
clear; clc; close all;

%% ---- DATA ---------------------------------------------------------------
metrics = {'Global Accuracy (Top-1)', 'Top-3 Accuracy', ...
           'Weighted Precision',      'Weighted F1-Score'};

baseline_vals  = [35.63, 72.0,  38.45, 35.63];
optimized_vals = [57.00, 92.45, 61.00, 58.00];
improvement    = optimized_vals - baseline_vals;   % absolute gain

% Percent improvement relative to baseline
pct_gain = (optimized_vals - baseline_vals) ./ baseline_vals * 100;

%% ---- FIGURE 8: Grouped Bar — Baseline vs. Optimized --------------------
fig8 = figure('Name', 'Fig8 Model Improvement', 'NumberTitle', 'off', ...
              'Position', [60, 60, 960, 560]);

data_mat = [baseline_vals; optimized_vals]';   % 4x2
b8 = bar(data_mat, 'grouped');
b8(1).FaceColor = [0.70, 0.70, 0.70];   % grey  — baseline
b8(2).FaceColor = [0.15, 0.72, 0.35];   % green — optimized

set(gca, 'XTickLabel', metrics, 'FontSize', 11, ...
         'TickLabelInterpreter', 'none');
xtickangle(10);
ylim([0, 105]);
ylabel('Score (%)', 'FontSize', 13);
title({'CatBoost Crop Classifier — Model Improvement: Baseline vs. V2 Optimized', ...
       'Bayesian Hyperparameter Search + Feature Interaction Engineering'}, ...
      'FontSize', 12, 'FontWeight', 'bold');
legend({'Baseline (V1)', 'Optimized (V2.1.0)'}, 'Location', 'northwest', 'FontSize', 11);
grid on; box on;
yline(100, '--k', 'LineWidth', 1);

% Annotate each bar
for i = 1:4
    % Baseline bar
    text(b8(1).XEndPoints(i), b8(1).YEndPoints(i) + 1.5, ...
         sprintf('%.1f%%', baseline_vals(i)), ...
         'HorizontalAlignment', 'center', 'FontSize', 9, 'Color', [0.3 0.3 0.3]);
    % Optimized bar
    text(b8(2).XEndPoints(i), b8(2).YEndPoints(i) + 1.5, ...
         sprintf('%.1f%%', optimized_vals(i)), ...
         'HorizontalAlignment', 'center', 'FontSize', 9, 'FontWeight', 'bold', ...
         'Color', [0 0.4 0.1]);
end

% Add improvement arrows / labels
for i = 1:4
    mid_x = (b8(1).XEndPoints(i) + b8(2).XEndPoints(i)) / 2;
    top_y = max(baseline_vals(i), optimized_vals(i)) + 8;
    text(mid_x, top_y, sprintf('+%.1f%%', improvement(i)), ...
         'HorizontalAlignment', 'center', 'FontSize', 9, ...
         'Color', [0.8 0.1 0.1], 'FontWeight', 'bold');
end

print(fig8, 'fig8_model_improvement_grouped', '-dpng', '-r300');
fprintf('Saved: fig8_model_improvement_grouped.png\n');

%% ---- FIGURE 9: Percentage Gain Bar Chart --------------------------------
fig9 = figure('Name', 'Fig9 Pct Gain', 'NumberTitle', 'off', ...
              'Position', [80, 80, 880, 480]);

bar_cols9 = [0.20, 0.52, 0.90;
             0.15, 0.72, 0.35;
             0.95, 0.40, 0.15;
             0.70, 0.28, 0.82];

b9 = bar(pct_gain, 'FaceColor', 'flat');
for i = 1:4
    b9.CData(i,:) = bar_cols9(i,:);
end

set(gca, 'XTickLabel', metrics, 'FontSize', 11, ...
         'TickLabelInterpreter', 'none');
xtickangle(10);
ylim([0, 75]);
ylabel('Relative Improvement (%)', 'FontSize', 13);
title({'Optimization Gain — Relative Improvement of V2 over Baseline', ...
       '(Each metric: (V2 - Baseline) / Baseline × 100)'}, ...
      'FontSize', 12, 'FontWeight', 'bold');
grid on; box on;

for i = 1:4
    text(i, pct_gain(i) + 1.5, sprintf('+%.1f%%', pct_gain(i)), ...
         'HorizontalAlignment', 'center', 'FontSize', 11, 'FontWeight', 'bold');
end

print(fig9, 'fig9_optimization_gain', '-dpng', '-r300');
fprintf('Saved: fig9_optimization_gain.png\n');

%% ---- IMPROVEMENT MATRIX (Console) --------------------------------------
fprintf('\n================================================================\n');
fprintf('  CROP CLASSIFIER — BASELINE vs. OPTIMIZED V2 COMPARISON\n');
fprintf('================================================================\n');
fprintf('%-26s  %-10s  %-12s  %-10s  %-10s\n', ...
        'Metric', 'Baseline', 'Optimized', 'Abs Gain', 'Pct Gain');
fprintf('%s\n', repmat('-', 1, 73));
for i = 1:4
    fprintf('%-26s  %-10.2f  %-12.2f  %-10.2f  +%-9.1f\n', ...
            metrics{i}, baseline_vals(i), optimized_vals(i), improvement(i), pct_gain(i));
end
fprintf('================================================================\n');
fprintf('  Average absolute improvement across 4 metrics: +%.2f%%\n', mean(improvement));
fprintf('  Average relative improvement across 4 metrics: +%.1f%%\n', mean(pct_gain));
fprintf('\n  Optimization techniques applied:\n');
fprintf('    1. Bayesian Hyperparameter Search (vs. Grid Search)\n');
fprintf('    2. Feature Interaction Engineering (N×pH, P×pH, SFI, Climate Index)\n');
fprintf('    3. 5-Fold Stratified Cross-Validation\n');
fprintf('    4. Class-weight balancing\n');
fprintf('================================================================\n\n');
