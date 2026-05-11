% =========================================================
% Chart 1 of 2: Crop Classifier — CatBoost V1 vs V2
% Same task (9-class crop recommendation), two training iterations.
% V1 = no feature engineering, basic hyperparameters
% V2 = + 7 interaction features + 3-trial grid search
% =========================================================

models = {'CatBoost V1', 'CatBoost V2'};
x      = 1:2;
w      = 0.4;
grey   = [0.70 0.70 0.70];
green  = [0.47 0.67 0.19];
palette = [grey; green];

top1_acc = [0.356, 0.570];
top3_acc = [0.760, 0.924];
macro_f1 = [0.350, 0.580];
macro_p  = [0.360, 0.620];
macro_r  = [0.350, 0.600];

fig = figure('Name','Crop Classifier V1 vs V2','Position',[100 100 880 500]);

subplot(1,3,1);
b = bar(x, top1_acc*100, w, 'FaceColor','flat','EdgeColor','none');
b.CData = palette;
xticks(x); xticklabels(models);
ylabel('Accuracy (%)'); ylim([0 72]);
title('Top-1 Accuracy','FontWeight','bold');
for i = x
    text(i, top1_acc(i)*100+1.5, sprintf('%.1f%%', top1_acc(i)*100), ...
        'HorizontalAlignment','center','FontSize',10,'FontWeight','bold');
end
set(gca,'Box','off','YGrid','on','GridAlpha',0.3);

subplot(1,3,2);
b = bar(x, top3_acc*100, w, 'FaceColor','flat','EdgeColor','none');
b.CData = palette;
xticks(x); xticklabels(models);
ylabel('Accuracy (%)'); ylim([60 100]);
title('Top-3 Accuracy','FontWeight','bold');
for i = x
    text(i, top3_acc(i)*100+0.8, sprintf('%.1f%%', top3_acc(i)*100), ...
        'HorizontalAlignment','center','FontSize',10,'FontWeight','bold');
end
set(gca,'Box','off','YGrid','on','GridAlpha',0.3);

subplot(1,3,3);
bar_data = [macro_p; macro_r; macro_f1]';
b = bar(x, bar_data, 0.6, 'EdgeColor','none');
b(1).FaceColor = [0.20 0.47 0.75];
b(2).FaceColor = [0.85 0.33 0.10];
b(3).FaceColor = [0.47 0.67 0.19];
% shade V1 bars
for k = 1:3; b(k).FaceAlpha = [0.5, 1.0]; end
xticks(x); xticklabels(models);
ylabel('Score'); ylim([0 0.75]);
title('Macro Precision / Recall / F1','FontWeight','bold');
legend(b, {'Precision','Recall','F1'}, 'Location','northwest','FontSize',8);
set(gca,'Box','off','YGrid','on','GridAlpha',0.3);

sgtitle({'Crop Classifier: CatBoost V1 vs CatBoost V2';
         'Same task — 9-class Nigerian crop recommendation';
         'Improvement: feature engineering + hyperparameter grid search'}, ...
        'FontSize',11,'FontWeight','bold');

saveas(fig, 'classifier_v1_vs_v2.png');
fprintf('Saved: classifier_v1_vs_v2.png\n');
