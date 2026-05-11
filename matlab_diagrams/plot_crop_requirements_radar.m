% =========================================================
% Crop Requirements Radar Chart
% Data: data/crop_requirements.json (mid-range values)
% =========================================================
% Dimensions: pH | Nitrogen | Phosphorus | Potassium | Temp | Rainfall
% Normalised 0-1 across all crops for each dimension

crops = {'Rice','Maize','Cassava','Tomato','Yam','Beans','Sorghum','Pepper','Onions'};

% Mid-range values from crop_requirements.json
%              pH     N      P      K     Temp   Rainfall
raw = [
    6.25,  30.5,  17.0,  127.5,  26.5,  1342;   % Rice
    6.30,  30.0,  16.5,  121.0,  26.5,  1276;   % Maize
    6.30,  30.5,  17.0,  121.0,  26.5,  1375;   % Cassava
    6.20,  30.5,  16.0,  122.0,  27.0,  1329;   % Tomato
    6.25,  31.0,  17.5,  126.0,  26.5,  1364;   % Yam
    6.20,  30.5,  17.0,  123.5,  26.5,  1251;   % Beans
    6.20,  30.5,  17.0,  127.5,  26.5,  1276;   % Sorghum
    6.25,  31.0,  17.0,  124.0,  26.5,  1314;   % Pepper
    6.25,  30.0,  17.0,  123.5,  26.5,  1262;   % Onions
];

% Min-max normalise each column
mn  = min(raw);
mx  = max(raw);
rng = mx - mn;
rng(rng == 0) = 1;  % avoid division by zero
norm_data = (raw - mn) ./ rng;

dim_labels = {'pH','Nitrogen (N)','Phosphorus (P)','Potassium (K)','Temperature','Rainfall'};
n_dim = numel(dim_labels);
n_crops = numel(crops);

% Close the polygon by repeating first column
theta = linspace(0, 2*pi, n_dim+1);
theta(end) = theta(1);

% Colours
cmap = lines(n_crops);

fig = figure('Name','Crop Requirements Radar','Position',[100 100 800 700]);
ax = axes('XColor','none','YColor','none');
hold(ax,'on');
axis(ax,'equal');
axis(ax,[-1.35 1.35 -1.35 1.35]);

% Draw grid circles at 0.25, 0.5, 0.75, 1.0
for r_val = [0.25 0.5 0.75 1.0]
    th = linspace(0, 2*pi, 200);
    plot(ax, r_val*cos(th), r_val*sin(th), '-', ...
         'Color',[0.8 0.8 0.8],'LineWidth',0.5);
    if r_val < 1.0
        text(ax, 0, r_val+0.03, sprintf('%.2f', r_val), ...
             'HorizontalAlignment','center','FontSize',7,'Color',[0.5 0.5 0.5]);
    end
end

% Draw axis spokes and labels
for d = 1:n_dim
    th_d = theta(d);
    plot(ax, [0 cos(th_d)], [0 sin(th_d)], '-', ...
         'Color',[0.6 0.6 0.6],'LineWidth',0.8);
    offset = 1.18;
    text(ax, offset*cos(th_d), offset*sin(th_d), dim_labels{d}, ...
         'HorizontalAlignment','center','FontSize',10,'FontWeight','bold');
end

% Plot each crop
lh = gobjects(n_crops,1);
for c = 1:n_crops
    vals = [norm_data(c,:), norm_data(c,1)];
    x = vals .* cos(theta);
    y = vals .* sin(theta);
    lh(c) = plot(ax, x, y, '-o', 'Color', cmap(c,:), ...
                 'LineWidth', 1.8, 'MarkerSize', 5, ...
                 'MarkerFaceColor', cmap(c,:));
end

legend(ax, lh, crops, 'Location','northeastoutside','FontSize',9);
title(ax, {'Crop Ideal Requirements — Radar Chart';
           'Normalised [0-1] from crop\_requirements.json'}, ...
          'FontSize',12,'FontWeight','bold');

hold(ax,'off');

saveas(fig, 'crop_requirements_radar.png');
fprintf('Saved: crop_requirements_radar.png\n');
