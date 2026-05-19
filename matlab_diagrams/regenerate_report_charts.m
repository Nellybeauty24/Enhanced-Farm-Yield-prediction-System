% Regenerate report charts from current model evaluation data.
% Run from the repository root:
%   cd('C:\Users\Nnenna\Documents\Project\SoilNutritionBackend')
%   run('matlab_diagrams/regenerate_report_charts.m')

clear; clc; close all;

dataDir = fullfile('matlab_diagrams', 'chart_data');
outDir = 'new_diagrams';
if ~exist(outDir, 'dir')
    mkdir(outDir);
end

fprintf('Regenerating MATLAB report charts from %s\n', dataDir);

%% Crop feature importance
cropImp = readtable(fullfile(dataDir, 'crop_feature_importance_v3.csv'), 'TextType', 'string');
figure('Color', 'w', 'Position', [100 100 1100 750]);
barh(categorical(flip(cropImp.Feature)), flip(cropImp.Importance), 'FaceColor', [0.18 0.55 0.45]);
grid on;
title('Top 15 Drivers of Crop Recommendation', 'FontWeight', 'bold');
xlabel('Relative Feature Importance (%)');
exportgraphics(gcf, fullfile(outDir, 'crop_feature_importance_v3.png'), 'Resolution', 300);

%% Yield feature importance
yieldImp = readtable(fullfile(dataDir, 'yield_feature_importance_v3.csv'), 'TextType', 'string');
figure('Color', 'w', 'Position', [100 100 1100 750]);
barh(categorical(flip(yieldImp.Feature)), flip(yieldImp.Importance), 'FaceColor', [0.79 0.33 0.22]);
grid on;
title('Top 15 Drivers of Harvest Yield', 'FontWeight', 'bold');
xlabel('Relative Feature Importance (%)');
exportgraphics(gcf, fullfile(outDir, 'yield_feature_importance_v3.png'), 'Resolution', 300);

%% Actual vs predicted yield
yp = readtable(fullfile(dataDir, 'yield_actual_vs_predicted_v3.csv'));
figure('Color', 'w', 'Position', [100 100 850 750]);
scatter(yp.Actual, yp.Predicted, 28, [0.16 0.62 0.56], 'filled', 'MarkerFaceAlpha', 0.55);
hold on;
limits = [min([yp.Actual; yp.Predicted]), max([yp.Actual; yp.Predicted])];
plot(limits, limits, '--', 'Color', [0.91 0.43 0.32], 'LineWidth', 2.2);
grid on;
title('Yield Prediction Accuracy', 'FontWeight', 'bold');
xlabel('Actual Recorded Yield (kg/ha)');
ylabel('Model Predicted Yield (kg/ha)');
legend({'Predictions', 'Perfect Prediction'}, 'Location', 'best');
exportgraphics(gcf, fullfile(outDir, 'yield_actual_vs_predicted_v3.png'), 'Resolution', 300);

%% Confusion matrix
cm = readtable(fullfile(dataDir, 'confusion_matrix_v3.csv'), 'ReadRowNames', true, 'TextType', 'string');
labels = string(cm.Properties.RowNames);
figure('Color', 'w', 'Position', [100 100 1000 850]);
h = heatmap(labels, labels, table2array(cm), 'Colormap', parula);
h.Title = 'Crop Classification Confusion Matrix';
h.XLabel = 'Predicted Crop';
h.YLabel = 'Actual Crop';
exportgraphics(gcf, fullfile(outDir, 'confusion_matrix_v3.png'), 'Resolution', 300);

%% Per-class performance
perf = readtable(fullfile(dataDir, 'per_class_performance_v3.csv'), 'TextType', 'string');
figure('Color', 'w', 'Position', [100 100 1200 700]);
bar(categorical(perf.Crop), [perf.Precision perf.Recall perf.F1Score]);
ylim([0 1.05]);
grid on;
title('Per-Class Performance Metrics (Precision, Recall, F1-Score)', 'FontWeight', 'bold');
ylabel('Score');
legend({'Precision', 'Recall', 'F1-Score'}, 'Location', 'southoutside', 'Orientation', 'horizontal');
exportgraphics(gcf, fullfile(outDir, 'per_class_performance_v3.png'), 'Resolution', 300);

%% Model improvement comparison
improve = readtable(fullfile(dataDir, 'model_improvement_comparison.csv'), 'TextType', 'string');
figure('Color', 'w', 'Position', [100 100 950 650]);
x = categorical(improve.Version);
plot(x, improve.CropAccuracy, '-o', 'LineWidth', 2.5, 'MarkerSize', 8);
hold on;
plot(x, improve.YieldR2, '-o', 'LineWidth', 2.5, 'MarkerSize', 8);
ylim([0 110]);
grid on;
title('Model Performance Leap Across Versions', 'FontWeight', 'bold');
ylabel('Accuracy / R2 Score (%)');
legend({'Crop Accuracy (%)', 'Yield R2 Score (%)'}, 'Location', 'best');
exportgraphics(gcf, fullfile(outDir, 'model_improvement_comparison.png'), 'Resolution', 300);

%% Cross-validation stability
cv = readtable(fullfile(dataDir, 'cross_validation_results_v3.csv'));
figure('Color', 'w', 'Position', [100 100 1000 600]);
bar(categorical("Fold " + string(cv.Fold)), [cv.CropAccuracy cv.YieldR2]);
ylim([90 102]);
grid on;
title('5-Fold Cross Validation Stability', 'FontWeight', 'bold');
ylabel('Score (%)');
legend({'Crop Classification Accuracy', 'Yield Regressor R2'}, 'Location', 'southoutside', 'Orientation', 'horizontal');
exportgraphics(gcf, fullfile(outDir, 'cross_validation_results_v3.png'), 'Resolution', 300);

%% Yield error metrics
err = readtable(fullfile(dataDir, 'yield_error_metrics.csv'), 'TextType', 'string');
figure('Color', 'w', 'Position', [100 100 1100 520]);
tiledlayout(1, 2);
nexttile;
bar(categorical(err.Metric(1:2)), err.Value(1:2), 'FaceColor', [0.82 0.36 0.23]);
grid on;
title('Absolute Yield Errors (kg/ha)', 'FontWeight', 'bold');
ylabel('Kilograms per Hectare');
nexttile;
bar(categorical(err.Metric(3:4)), err.Value(3:4), 'FaceColor', [0.18 0.55 0.45]);
grid on;
title('Relative Accuracy Metrics', 'FontWeight', 'bold');
ylabel('Percentage (%)');
exportgraphics(gcf, fullfile(outDir, 'yield_error_metrics.png'), 'Resolution', 300);

fprintf('Done. MATLAB report charts saved in %s\n', outDir);
