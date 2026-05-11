% =========================================================================
% SCRIPT 2: script_2_yield_cv_results.m
% Yield Prediction Model — 5-Fold Cross-Validation Results
% -------------------------------------------------------------------------
% Model  : CatBoost Regressor
% Target : yield_kg_ha (kg per hectare)
% Dataset: Nigeria Agricultural Multi-Environmental Dataset (20,000 records)
% Source : outputs/cv_results.csv (exact values preserved)
% =========================================================================
clear; clc; close all;

%% ---- DATA (from outputs/cv_results.csv — exact values) -----------------
folds = (1:5)';

rmse = [2222.554321171821; ...
        2161.427971718228; ...
        2146.143823897956; ...
        2130.197324707043; ...
        2114.553053787001];

mae  = [1449.6141746541407; ...
        1433.5188303063721; ...
        1431.9774783291782; ...
        1416.8886065897743; ...
        1426.5540895258496];

r2   = [0.7241785599862068; ...
        0.7179864669857451; ...
        0.7262296817293729; ...
        0.7182115384552140; ...
        0.7303240624557328];

mape_pct = [36.682569183309177; ...   % stored as percent (×100)
            37.677270982302663; ...
            36.166289325625920; ...
            36.913931203637480; ...
            38.205055497700974];

% Summary statistics
m_rmse = mean(rmse);  s_rmse = std(rmse);
m_mae  = mean(mae);   s_mae  = std(mae);
m_r2   = mean(r2);    s_r2   = std(r2);
m_mape = mean(mape_pct); s_mape = std(mape_pct);

%% ---- FIGURE 3: 2×2 Subplots — All CV Metrics per Fold ------------------
fig3 = figure('Name', 'Fig3 Yield CV Results', 'NumberTitle', 'off', ...
              'Position', [40, 40, 1120, 800]);

% Colours
c_rmse = [0.20, 0.52, 0.90];
c_mae  = [0.95, 0.40, 0.15];
c_r2   = [0.15, 0.72, 0.35];
c_mape = [0.70, 0.28, 0.82];

% -- RMSE --
subplot(2, 2, 1);
bar(folds, rmse, 'FaceColor', c_rmse, 'EdgeColor', 'none');
hold on;
yline(m_rmse, '--r', 'LineWidth', 2);
hold off;
text(5.35, m_rmse + 4, sprintf('Mean = %.0f', m_rmse), ...
     'Color', [0.8 0 0], 'FontSize', 9, 'FontWeight', 'bold');
xticks(1:5); xlim([0.3, 5.7]); ylim([2060, 2280]);
xlabel('Fold', 'FontSize', 11); ylabel('RMSE (kg/ha)', 'FontSize', 11);
title('Root Mean Squared Error (RMSE)', 'FontSize', 12, 'FontWeight', 'bold');
grid on; box on;
for i = 1:5
    text(i, rmse(i) + 4, sprintf('%.0f', rmse(i)), ...
         'HorizontalAlignment', 'center', 'FontSize', 9);
end

% -- MAE --
subplot(2, 2, 2);
bar(folds, mae, 'FaceColor', c_mae, 'EdgeColor', 'none');
hold on;
yline(m_mae, '--r', 'LineWidth', 2);
hold off;
text(5.35, m_mae + 1, sprintf('Mean = %.1f', m_mae), ...
     'Color', [0.8 0 0], 'FontSize', 9, 'FontWeight', 'bold');
xticks(1:5); xlim([0.3, 5.7]); ylim([1395, 1465]);
xlabel('Fold', 'FontSize', 11); ylabel('MAE (kg/ha)', 'FontSize', 11);
title('Mean Absolute Error (MAE)', 'FontSize', 12, 'FontWeight', 'bold');
grid on; box on;
for i = 1:5
    text(i, mae(i) + 0.8, sprintf('%.1f', mae(i)), ...
         'HorizontalAlignment', 'center', 'FontSize', 9);
end

% -- R² --
subplot(2, 2, 3);
bar(folds, r2, 'FaceColor', c_r2, 'EdgeColor', 'none');
hold on;
yline(m_r2, '--r', 'LineWidth', 2);
hold off;
text(5.35, m_r2 + 0.0003, sprintf('Mean = %.4f', m_r2), ...
     'Color', [0.8 0 0], 'FontSize', 9, 'FontWeight', 'bold');
xticks(1:5); xlim([0.3, 5.7]); ylim([0.708, 0.737]);
xlabel('Fold', 'FontSize', 11); ylabel('R² Score', 'FontSize', 11);
title('Coefficient of Determination (R²)', 'FontSize', 12, 'FontWeight', 'bold');
grid on; box on;
for i = 1:5
    text(i, r2(i) + 0.0003, sprintf('%.4f', r2(i)), ...
         'HorizontalAlignment', 'center', 'FontSize', 9);
end

% -- MAPE --
subplot(2, 2, 4);
bar(folds, mape_pct, 'FaceColor', c_mape, 'EdgeColor', 'none');
hold on;
yline(m_mape, '--r', 'LineWidth', 2);
hold off;
text(5.35, m_mape + 0.1, sprintf('Mean = %.2f%%', m_mape), ...
     'Color', [0.8 0 0], 'FontSize', 9, 'FontWeight', 'bold');
xticks(1:5); xlim([0.3, 5.7]); ylim([34.5, 40.0]);
xlabel('Fold', 'FontSize', 11); ylabel('MAPE (%)', 'FontSize', 11);
title('Mean Absolute Percentage Error (MAPE)', 'FontSize', 12, 'FontWeight', 'bold');
grid on; box on;
for i = 1:5
    text(i, mape_pct(i) + 0.08, sprintf('%.2f%%', mape_pct(i)), ...
         'HorizontalAlignment', 'center', 'FontSize', 9);
end

sgtitle({'Yield Prediction Model (CatBoost Regressor)', ...
         '5-Fold Stratified Cross-Validation — All Metrics'}, ...
        'FontSize', 14, 'FontWeight', 'bold');

print(fig3, 'fig3_yield_cv_results', '-dpng', '-r300');
fprintf('Saved: fig3_yield_cv_results.png\n');

%% ---- FIGURE 4: Error Bar Summary Chart ----------------------------------
fig4 = figure('Name', 'Fig4 CV Summary', 'NumberTitle', 'off', ...
              'Position', [80, 80, 880, 500]);

% Normalise for side-by-side comparison
m_vals = [m_rmse/1000, m_mae/1000, m_r2*100, m_mape];
s_vals = [s_rmse/1000, s_mae/1000, s_r2*100, s_mape];
xlbls  = {'RMSE (÷1000 kg/ha)', 'MAE (÷1000 kg/ha)', 'R² (×100)', 'MAPE (%)'};
bcolors = [c_rmse; c_mae; c_r2; c_mape];

b4 = bar(m_vals, 'FaceColor', 'flat');
for i = 1:4
    b4.CData(i,:) = bcolors(i,:);
end
hold on;
errorbar(1:4, m_vals, s_vals, '.k', 'LineWidth', 2, 'CapSize', 12);
hold off;

set(gca, 'XTickLabel', xlbls, 'FontSize', 11, 'TickLabelInterpreter', 'none');
ylabel('Metric Value (scaled)', 'FontSize', 13);
title({'Yield Prediction Model — Cross-Validation Summary', ...
       'Mean ± 1 Std Dev across 5 folds (metrics scaled for comparison)'}, ...
      'FontSize', 12, 'FontWeight', 'bold');
grid on; box on;

for i = 1:4
    text(i, m_vals(i) + s_vals(i) + 0.15, ...
         sprintf('%.3f\n±%.3f', m_vals(i), s_vals(i)), ...
         'HorizontalAlignment', 'center', 'FontSize', 9, 'FontWeight', 'bold');
end

print(fig4, 'fig4_cv_summary', '-dpng', '-r300');
fprintf('Saved: fig4_cv_summary.png\n');

%% ---- EVALUATION MATRIX (Console Output) ---------------------------------
fprintf('\n================================================================\n');
fprintf('  YIELD PREDICTION — 5-FOLD CROSS-VALIDATION EVALUATION MATRIX\n');
fprintf('================================================================\n');
fprintf('%-6s  %-14s  %-14s  %-10s  %-10s\n', ...
        'Fold', 'RMSE (kg/ha)', 'MAE (kg/ha)', 'R²', 'MAPE (%)');
fprintf('%s\n', repmat('-', 1, 60));
for i = 1:5
    fprintf('%-6d  %-14.4f  %-14.4f  %-10.6f  %-10.6f\n', ...
            i, rmse(i), mae(i), r2(i), mape_pct(i));
end
fprintf('%s\n', repmat('-', 1, 60));
fprintf('%-6s  %-14.4f  %-14.4f  %-10.6f  %-10.6f\n', ...
        'Mean', m_rmse, m_mae, m_r2, m_mape);
fprintf('%-6s  %-14.4f  %-14.4f  %-10.6f  %-10.6f\n', ...
        'Std',  s_rmse, s_mae, s_r2, s_mape);
fprintf('%-6s  %-14.2f  %-14.2f  %-10.4f  %-10.4f\n', ...
        'CV%%', s_rmse/m_rmse*100, s_mae/m_mae*100, s_r2/m_r2*100, s_mape/m_mape*100);
fprintf('================================================================\n');
fprintf('  Variance Explained (mean R²): %.2f%%\n', m_r2*100);
fprintf('  Avg Yield Error (RMSE)      : ±%.0f kg/ha\n', m_rmse);
fprintf('================================================================\n\n');
