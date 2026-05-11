% =========================================================================
% run_all_scripts.m
% Master runner — executes all 6 evaluation scripts for SoilNutritionBackend
% -------------------------------------------------------------------------
% USAGE:
%   1. Open MATLAB
%   2. Set the Current Folder to this 'matlab_outputs' directory
%      (or run:  cd('C:\Users\Nnenna\Documents\Project\SoilNutritionBackend\matlab_outputs') )
%   3. Run this script: run_all_scripts
%   4. All PNG figures will be saved in this same folder
%
% REQUIRES: MATLAB R2019b or later (uses XEndPoints, YEndPoints, sgtitle)
% =========================================================================
clear; clc; close all;

fprintf('=============================================================\n');
fprintf('  SoilNutritionBackend — MATLAB Evaluation Suite\n');
fprintf('  Generating all diagrams and evaluation matrices...\n');
fprintf('=============================================================\n\n');

scripts = { ...
    'script_1_crop_classification_metrics.m',   ...
    'script_2_yield_cv_results.m',              ...
    'script_3_feature_importance_crop.m',       ...
    'script_4_feature_importance_yield.m',      ...
    'script_5_model_improvement_comparison.m',  ...
    'script_6_crop_soil_requirements.m'         };

descriptions = { ...
    'Crop model per-class metrics & overall accuracy', ...
    'Yield model 5-fold cross-validation results',     ...
    'Crop model top-5 feature importance',             ...
    'Yield model full feature importance (all 20)',    ...
    'Baseline vs. V2 optimized model comparison',      ...
    'Optimal soil & climate requirements (9 crops)'    };

t_total = tic;
for i = 1 : length(scripts)
    fprintf('[%d/%d] Running: %s\n', i, length(scripts), descriptions{i});
    t0 = tic;
    run(scripts{i});
    fprintf('       Completed in %.1f s\n\n', toc(t0));
end

fprintf('=============================================================\n');
fprintf('  All scripts completed in %.1f seconds.\n', toc(t_total));
fprintf('=============================================================\n\n');

%% List all generated PNG files
pngs = dir('*.png');
if isempty(pngs)
    fprintf('WARNING: No PNG files found. Check that scripts ran without error.\n');
else
    fprintf('Generated files (%d PNGs):\n', length(pngs));
    for i = 1:length(pngs)
        fprintf('  fig%02d — %s\n', i, pngs(i).name);
    end
end

fprintf('\nAll figures also remain open — use "Save As" from each figure window\n');
fprintf('to export in other formats (SVG, EPS, PDF, TIFF).\n');
