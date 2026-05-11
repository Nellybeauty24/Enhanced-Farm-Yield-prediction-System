% =========================================================
% Master Script — Run All Soil Nutrition Backend Diagrams
% Output files are saved as PNG in the current folder.
%
% USAGE:
%   1. Open MATLAB
%   2. cd to this folder (matlab_diagrams/)
%   3. Run: run_all_diagrams
%
% OUTPUTS (7 PNG files):
%   confusion_matrix.png
%   classification_report.png
%   feature_importance_crop.png
%   feature_importance_yield.png
%   cv_results_yield.png
%   yield_cv_scatter.png
%   crop_requirements_radar.png
%   evaluation_matrix.png
%   model_comparison.png
% =========================================================

fprintf('\n================================================\n');
fprintf(' Soil Nutrition Backend — MATLAB Diagram Suite\n');
fprintf('================================================\n\n');

scripts = {
    'plot_confusion_matrix',
    'plot_classification_report',
    'plot_feature_importance_crop',
    'plot_feature_importance_yield',
    'plot_cv_results_yield',
    'plot_yield_cv_scatter',
    'plot_crop_requirements_radar',
    'evaluation_matrix_table',
    'plot_model_comparison'
};

for i = 1:numel(scripts)
    fprintf('[%d/%d] Running %s ...\n', i, numel(scripts), scripts{i});
    try
        run(scripts{i});
    catch ME
        fprintf('  ERROR in %s: %s\n', scripts{i}, ME.message);
    end
    close all;  % close figures between runs to free memory
end

fprintf('\n================================================\n');
fprintf(' Done. Check current folder for PNG output files.\n');
fprintf('================================================\n');
