% =========================================================
% 5-Fold Cross-Validation Results — Yield Prediction Model
% Exact values from outputs/cv_results.csv
% =========================================================

folds = 1:5;

rmse = [2222.554, 2161.428, 2146.144, 2130.197, 2114.553];
mae  = [1449.614, 1433.519, 1431.977, 1416.889, 1426.554];
r2   = [0.7242,   0.7180,   0.7262,   0.7182,   0.7303];
mape = [0.3668,   0.3768,   0.3617,   0.3691,   0.3821];

mean_rmse = mean(rmse); mean_mae = mean(mae);
mean_r2   = mean(r2);   mean_mape = mean(mape);

fig = figure('Name','CV Results Yield','Position',[100 100 950 700]);

% ---- RMSE ----
subplot(2,2,1);
bar(folds, rmse, 'FaceColor',[0.20 0.47 0.75],'EdgeColor','none');
hold on;
yline(mean_rmse,'--r','LineWidth',1.5);
text(4.6, mean_rmse+20, sprintf('Mean: %.0f', mean_rmse),'Color','r','FontSize',9);
xticks(folds); xlabel('Fold'); ylabel('RMSE (kg/ha)');
title('Root Mean Squared Error','FontWeight','bold');
ylim([2000 2350]);
for i = folds
    text(i, rmse(i)+15, sprintf('%.0f',rmse(i)),'HorizontalAlignment','center','FontSize',8);
end
set(gca,'Box','off','YGrid','on','GridAlpha',0.3);
hold off;

% ---- MAE ----
subplot(2,2,2);
bar(folds, mae, 'FaceColor',[0.85 0.33 0.10],'EdgeColor','none');
hold on;
yline(mean_mae,'--r','LineWidth',1.5);
text(4.6, mean_mae+8, sprintf('Mean: %.0f', mean_mae),'Color','r','FontSize',9);
xticks(folds); xlabel('Fold'); ylabel('MAE (kg/ha)');
title('Mean Absolute Error','FontWeight','bold');
ylim([1380 1480]);
for i = folds
    text(i, mae(i)+3, sprintf('%.0f',mae(i)),'HorizontalAlignment','center','FontSize',8);
end
set(gca,'Box','off','YGrid','on','GridAlpha',0.3);
hold off;

% ---- R² ----
subplot(2,2,3);
bar(folds, r2, 'FaceColor',[0.47 0.67 0.19],'EdgeColor','none');
hold on;
yline(mean_r2,'--r','LineWidth',1.5);
text(4.6, mean_r2+0.001, sprintf('Mean: %.4f', mean_r2),'Color','r','FontSize',9);
xticks(folds); xlabel('Fold'); ylabel('R²');
title('Coefficient of Determination','FontWeight','bold');
ylim([0.70 0.745]);
for i = folds
    text(i, r2(i)+0.0005, sprintf('%.4f',r2(i)),'HorizontalAlignment','center','FontSize',8);
end
set(gca,'Box','off','YGrid','on','GridAlpha',0.3);
hold off;

% ---- MAPE ----
subplot(2,2,4);
bar(folds, mape*100, 'FaceColor',[0.64 0.08 0.18],'EdgeColor','none');
hold on;
yline(mean_mape*100,'--r','LineWidth',1.5);
text(4.5, mean_mape*100+0.2, sprintf('Mean: %.1f%%', mean_mape*100),'Color','r','FontSize',9);
xticks(folds); xlabel('Fold'); ylabel('MAPE (%)');
title('Mean Absolute Percentage Error','FontWeight','bold');
ylim([35 40]);
for i = folds
    text(i, mape(i)*100+0.1, sprintf('%.1f%%',mape(i)*100),'HorizontalAlignment','center','FontSize',8);
end
set(gca,'Box','off','YGrid','on','GridAlpha',0.3);
hold off;

sgtitle({'5-Fold Cross-Validation — CatBoost Yield Regressor';
         sprintf('Avg RMSE: %.0f kg/ha | Avg MAE: %.0f kg/ha | Avg R²: %.4f | Avg MAPE: %.1f%%', ...
                 mean_rmse, mean_mae, mean_r2, mean_mape*100)}, ...
        'FontSize',11,'FontWeight','bold');

saveas(fig, 'cv_results_yield.png');
fprintf('Saved: cv_results_yield.png\n');
