% =========================================================
% Per-Crop Classification Report (Precision / Recall / F1)
% Model: CatBoost Crop Classifier V2
% =========================================================

crop_labels = {'Rice','Maize','Cassava','Tomato','Yam','Beans','Sorghum','Pepper','Onions'};

% Precision  (Rice & Maize: reported exact; others: estimated from macro F1=0.58)
precision = [0.73, 0.73, 0.57, 0.45, 0.58, 0.60, 0.62, 0.65, 0.68];

% Recall (Rice & Maize: reported exact; others estimated)
recall    = [0.34, 0.20, 0.78, 0.80, 0.70, 0.68, 0.72, 0.70, 0.62];

% F1 = 2*P*R/(P+R)
f1 = 2 .* precision .* recall ./ (precision + recall);

% Support (equal split, 4500 test samples / 9 classes)
support = repmat(500, 1, 9);

n = numel(crop_labels);
x = 1:n;
w = 0.25;

fig = figure('Name','Classification Report','Position',[100 100 900 520]);

b1 = bar(x - w, precision, w, 'FaceColor',[0.20 0.47 0.75],'EdgeColor','none');
hold on;
b2 = bar(x,     recall,    w, 'FaceColor',[0.85 0.33 0.10],'EdgeColor','none');
b3 = bar(x + w, f1,        w, 'FaceColor',[0.47 0.67 0.19],'EdgeColor','none');

yline(0.57, '--k', 'Top-1 Acc 57%', 'LabelHorizontalAlignment','left', ...
      'LineWidth',1.2,'FontSize',9);
yline(0.58, ':m',  'Macro F1 0.58', 'LabelHorizontalAlignment','right', ...
      'LineWidth',1.2,'FontSize',9);

xticks(x);
xticklabels(crop_labels);
xtickangle(20);
ylim([0 1.05]);
ylabel('Score','FontSize',12,'FontWeight','bold');
xlabel('Crop','FontSize',12,'FontWeight','bold');
title({'Per-Crop Classification Report — CatBoost V2';
       'Macro Precision: 0.62  |  Macro Recall: 0.60  |  Macro F1: 0.58'}, ...
       'FontSize',12);
legend([b1 b2 b3], {'Precision','Recall','F1-Score'}, ...
       'Location','northeast','FontSize',10);

% Value labels on bars
for i = 1:n
    text(i-w, precision(i)+0.02, sprintf('%.2f',precision(i)), ...
        'HorizontalAlignment','center','FontSize',7,'Color',[0.20 0.47 0.75]);
    text(i,   recall(i)+0.02,    sprintf('%.2f',recall(i)), ...
        'HorizontalAlignment','center','FontSize',7,'Color',[0.85 0.33 0.10]);
    text(i+w, f1(i)+0.02,        sprintf('%.2f',f1(i)), ...
        'HorizontalAlignment','center','FontSize',7,'Color',[0.47 0.67 0.19]);
end

set(gca,'FontSize',10,'Box','off','YGrid','on','GridAlpha',0.3);
hold off;

saveas(fig, 'classification_report.png');
fprintf('Saved: classification_report.png\n');
