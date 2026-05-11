% =========================================================================
% SCRIPT 6: script_6_crop_soil_requirements.m
% Optimal Soil & Climate Requirements for All 9 Supported Crops
% -------------------------------------------------------------------------
% Source : data/crop_requirements.json (exact values preserved)
% Crops  : Pepper, Beans, Sorghum, Maize, Yam, Onions, Rice, Cassava, Tomato
% Params : pH, Nitrogen (mg/kg), Phosphorus (mg/kg), Potassium (mg/kg),
%          Temperature (C), Rainfall (mm)
% =========================================================================
clear; clc; close all;

%% ---- DATA (from data/crop_requirements.json) ----------------------------
crops = {'Pepper','Beans','Sorghum','Maize','Yam','Onions','Rice','Cassava','Tomato'};
n = length(crops);

%  [min, max] for each parameter
ph_min  = [5.7, 5.6, 5.6, 5.7, 5.7, 5.6, 5.6, 5.7, 5.6];
ph_max  = [6.8, 6.8, 6.8, 6.9, 6.8, 6.9, 6.9, 6.9, 6.8];

n_min   = [21, 21, 21, 21, 21, 20, 22, 21, 21];
n_max   = [41, 40, 40, 39, 41, 40, 39, 40, 40];

p_min   = [11, 11, 11, 10, 11, 11, 11, 11, 10];
p_max   = [23, 23, 23, 23, 24, 23, 23, 23, 22];

k_min   = [90,  90,  91,  84,  88,  88,  92,  83,  87];
k_max   = [158, 157, 164, 158, 164, 159, 163, 159, 157];

t_min   = [24, 24, 24, 24, 24, 24, 24, 24, 25];
t_max   = [29, 29, 29, 29, 29, 29, 29, 29, 29];

r_min   = [982,  917,  914,  940,  1003, 925,  979,  1027, 976];
r_max   = [1645, 1584, 1638, 1611, 1725, 1599, 1705, 1722, 1681];

% Compute midpoints and half-ranges for error bars
ph_mid  = (ph_min  + ph_max)  / 2;   ph_err  = (ph_max  - ph_min)  / 2;
n_mid   = (n_min   + n_max)   / 2;   n_err   = (n_max   - n_min)   / 2;
p_mid   = (p_min   + p_max)   / 2;   p_err   = (p_max   - p_min)   / 2;
k_mid   = (k_min   + k_max)   / 2;   k_err   = (k_max   - k_min)   / 2;
t_mid   = (t_min   + t_max)   / 2;   t_err   = (t_max   - t_min)   / 2;
r_mid   = (r_min   + r_max)   / 2;   r_err   = (r_max   - r_min)   / 2;

x = 1:n;

%% ---- FIGURE 10: Soil Nutrient Ranges (N, P, K) — Error Bar Chart --------
fig10 = figure('Name', 'Fig10 Soil Nutrients NPK', 'NumberTitle', 'off', ...
               'Position', [40, 40, 1100, 560]);

data_npk = [n_mid; p_mid; k_mid]';   % 9×3
err_npk  = [n_err; p_err; k_err]';

b10 = bar(x, data_npk, 'grouped');
b10(1).FaceColor = [0.15, 0.72, 0.35];  % green  — N
b10(2).FaceColor = [0.95, 0.40, 0.15];  % orange — P
b10(3).FaceColor = [0.20, 0.52, 0.90];  % blue   — K

hold on;
% Error bars — compute x positions of each bar group
nGroups = n; nBars = 3;
gw = min(0.8, nBars / (nBars + 1.5));
for j = 1:nBars
    x_bar = x - gw/2 + (2*j-1) * gw / (2*nBars);
    errorbar(x_bar, data_npk(:,j)', err_npk(:,j)', ...
             '.k', 'LineWidth', 1.2, 'CapSize', 5);
end
hold off;

set(gca, 'XTickLabel', crops, 'FontSize', 11, 'TickLabelInterpreter', 'none');
xtickangle(0);
ylabel('Optimal Level (mg/kg)', 'FontSize', 13);
title({'Optimal Soil Nutrient Requirements by Crop', ...
       'Bars = midpoint of optimal range; Error bars = ±half-range'}, ...
      'FontSize', 12, 'FontWeight', 'bold');
legend({'Nitrogen (N)', 'Phosphorus (P)', 'Potassium (K)'}, ...
       'Location', 'northeast', 'FontSize', 11);
grid on; box on;

print(fig10, 'fig10_soil_nutrients_npk', '-dpng', '-r300');
fprintf('Saved: fig10_soil_nutrients_npk.png\n');

%% ---- FIGURE 11: Soil pH Range per Crop ----------------------------------
fig11 = figure('Name', 'Fig11 Soil pH', 'NumberTitle', 'off', ...
               'Position', [60, 60, 960, 480]);

bar(x, ph_mid, 'FaceColor', [0.55, 0.25, 0.78], 'EdgeColor', 'none');
hold on;
errorbar(x, ph_mid, ph_err, '.k', 'LineWidth', 1.5, 'CapSize', 8);
yline(7.0, '--k', 'Neutral pH=7', 'LineWidth', 1.2, 'FontSize', 10);
hold off;

set(gca, 'XTickLabel', crops, 'FontSize', 12, 'TickLabelInterpreter', 'none');
ylim([5.0, 8.0]);
yticks(5.0 : 0.5 : 8.0);
ylabel('Soil pH', 'FontSize', 13);
title({'Optimal Soil pH Range by Crop', ...
       'All 9 crops prefer slightly acidic to neutral soils (pH 5.6 – 6.9)'}, ...
      'FontSize', 12, 'FontWeight', 'bold');
grid on; box on;

for i = 1:n
    text(i, ph_max(i) + 0.06, ...
         sprintf('[%.1f–%.1f]', ph_min(i), ph_max(i)), ...
         'HorizontalAlignment', 'center', 'FontSize', 8.5);
end

print(fig11, 'fig11_soil_ph', '-dpng', '-r300');
fprintf('Saved: fig11_soil_ph.png\n');

%% ---- FIGURE 12: Rainfall Requirements per Crop --------------------------
fig12 = figure('Name', 'Fig12 Rainfall', 'NumberTitle', 'off', ...
               'Position', [60, 60, 980, 500]);

bar(x, r_mid, 'FaceColor', [0.20, 0.52, 0.90], 'EdgeColor', 'none');
hold on;
errorbar(x, r_mid, r_err, '.k', 'LineWidth', 1.5, 'CapSize', 8);
hold off;

set(gca, 'XTickLabel', crops, 'FontSize', 12, 'TickLabelInterpreter', 'none');
ylim([700, 1900]);
ylabel('Annual Rainfall (mm)', 'FontSize', 13);
title({'Optimal Annual Rainfall Requirements by Crop', ...
       'Bars = midpoint; Error bars = ±half-range (from crop_requirements.json)'}, ...
      'FontSize', 12, 'FontWeight', 'bold');
grid on; box on;

for i = 1:n
    text(i, r_max(i) + 30, sprintf('[%d–%d]', r_min(i), r_max(i)), ...
         'HorizontalAlignment', 'center', 'FontSize', 8, 'Rotation', 0);
end

print(fig12, 'fig12_rainfall_requirements', '-dpng', '-r300');
fprintf('Saved: fig12_rainfall_requirements.png\n');

%% ---- FIGURE 13: Radar / Spider Chart — Normalised Multi-Parameter -------
% Normalise all parameters to [0,1] for radar comparison (using combined min/max)
all_mins = [min(ph_min), min(n_min), min(p_min), min(k_min)/10, min(t_min), min(r_min)/100];
all_maxs = [max(ph_max), max(n_max), max(p_max), max(k_max)/10, max(t_max), max(r_max)/100];

norm_mid_raw = [ph_mid; n_mid; p_mid; k_mid/10; t_mid; r_mid/100]';  % 9×6
norm_mid = (norm_mid_raw - all_mins) ./ (all_maxs - all_mins);

param_labels = {'pH', 'Nitrogen', 'Phosphorus', 'Potassium (÷10)', 'Temp', 'Rainfall (÷100)'};
nParams = 6;

theta = linspace(0, 2*pi, nParams + 1);
theta = theta(1:end-1);

fig13 = figure('Name', 'Fig13 Radar Requirements', 'NumberTitle', 'off', ...
               'Position', [40, 40, 1200, 860]);

cmap13 = lines(n);

for crop_i = 1:n
    subplot_rows = 3; subplot_cols = 3;
    subplot(subplot_rows, subplot_cols, crop_i);

    vals = [norm_mid(crop_i,:), norm_mid(crop_i,1)];  % close the polygon
    t_all = [theta, theta(1)];

    [xx, yy] = pol2cart(t_all, vals);
    fill(xx, yy, cmap13(crop_i,:), 'FaceAlpha', 0.35, 'EdgeColor', cmap13(crop_i,:), 'LineWidth', 2);
    hold on;

    % Draw grid circles
    for r_grid = [0.25, 0.50, 0.75, 1.00]
        t_circ = linspace(0, 2*pi, 100);
        plot(r_grid * cos(t_circ), r_grid * sin(t_circ), '--', ...
             'Color', [0.7 0.7 0.7], 'LineWidth', 0.5);
    end

    % Draw spokes and labels
    for p_i = 1:nParams
        plot([0, cos(theta(p_i))], [0, sin(theta(p_i))], '-', ...
             'Color', [0.6 0.6 0.6], 'LineWidth', 0.8);
        lbl_x = 1.18 * cos(theta(p_i));
        lbl_y = 1.18 * sin(theta(p_i));
        text(lbl_x, lbl_y, param_labels{p_i}, ...
             'HorizontalAlignment', 'center', 'FontSize', 7.5, ...
             'TickLabelInterpreter', 'none');
    end

    hold off;
    axis equal; axis off;
    title(crops{crop_i}, 'FontSize', 11, 'FontWeight', 'bold');
    xlim([-1.4, 1.4]); ylim([-1.4, 1.4]);
end

sgtitle({'Crop Requirement Profiles — Normalised Radar Charts', ...
         'Parameters normalised across all 9 crops; larger area = higher requirements'}, ...
        'FontSize', 13, 'FontWeight', 'bold');

print(fig13, 'fig13_radar_crop_requirements', '-dpng', '-r300');
fprintf('Saved: fig13_radar_crop_requirements.png\n');

%% ---- REQUIREMENTS MATRIX (Console) -------------------------------------
fprintf('\n===============================================================================================\n');
fprintf('  CROP SOIL & CLIMATE REQUIREMENTS — FULL MATRIX (from crop_requirements.json)\n');
fprintf('===============================================================================================\n');
fprintf('%-10s  %-12s  %-14s  %-14s  %-14s  %-12s  %-20s\n', ...
        'Crop', 'pH', 'N (mg/kg)', 'P (mg/kg)', 'K (mg/kg)', 'Temp (C)', 'Rainfall (mm)');
fprintf('%s\n', repmat('-', 1, 100));
for i = 1:n
    fprintf('%-10s  [%.1f–%.1f]  [%2d–%2d]       [%2d–%2d]       [%3d–%3d]     [%2d–%2d]      [%4d–%4d]\n', ...
            crops{i}, ph_min(i), ph_max(i), n_min(i), n_max(i), ...
            p_min(i), p_max(i), k_min(i), k_max(i), ...
            t_min(i), t_max(i), r_min(i), r_max(i));
end
fprintf('===============================================================================================\n\n');
