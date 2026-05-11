% =========================================================
% Yield Model — CV Metrics Scatter + Error Bars
% Shows stability of the model across 5 folds
% =========================================================

folds = 1:5;

rmse = [2222.554, 2161.428, 2146.144, 2130.197, 2114.553];
mae  = [1449.614, 1433.519, 1431.977, 1416.889, 1426.554];
r2   = [0.7242,   0.7180,   0.7262,   0.7182,   0.7303];
mape = [36.68,    37.68,    36.17,    36.91,    38.21];

fig = figure('Name','CV Metrics Scatter','Position',[100 100 900 420]);

% ---- Left: RMSE and MAE over folds ----
subplot(1,2,1);
yyaxis left;
plot(folds, rmse, '-o', 'Color',[0.20 0.47 0.75], 'LineWidth',2, ...
     'MarkerSize',8, 'MarkerFaceColor',[0.20 0.47 0.75]);
ylabel('RMSE (kg/ha)','Color',[0.20 0.47 0.75],'FontSize',11);
ylim([2050 2350]);

yyaxis right;
plot(folds, mae, '--s', 'Color',[0.85 0.33 0.10], 'LineWidth',2, ...
     'MarkerSize',8, 'MarkerFaceColor',[0.85 0.33 0.10]);
ylabel('MAE (kg/ha)','Color',[0.85 0.33 0.10],'FontSize',11);
ylim([1370 1500]);

xticks(folds);
xlabel('Cross-Validation Fold','FontSize',11);
title({'RMSE & MAE per Fold';sprintf('RMSE trend: %.0f → %.0f  |  MAE trend: %.0f → %.0f', ...
       rmse(1),rmse(5),mae(1),mae(5))},'FontSize',10);
legend({'RMSE','MAE'},'Location','northeast','FontSize',9);
set(gca,'Box','off','XGrid','on','GridAlpha',0.3);

% ---- Right: R² and MAPE over folds ----
subplot(1,2,2);
yyaxis left;
plot(folds, r2, '-^', 'Color',[0.47 0.67 0.19], 'LineWidth',2, ...
     'MarkerSize',8, 'MarkerFaceColor',[0.47 0.67 0.19]);
ylabel('R²','Color',[0.47 0.67 0.19],'FontSize',11);
ylim([0.710 0.740]);

yyaxis right;
plot(folds, mape, '--d', 'Color',[0.64 0.08 0.18], 'LineWidth',2, ...
     'MarkerSize',8, 'MarkerFaceColor',[0.64 0.08 0.18]);
ylabel('MAPE (%)','Color',[0.64 0.08 0.18],'FontSize',11);
ylim([35 40]);

xticks(folds);
xlabel('Cross-Validation Fold','FontSize',11);
title({'R² & MAPE per Fold';sprintf('R² range: %.4f–%.4f  |  MAPE range: %.1f%%–%.1f%%', ...
       min(r2),max(r2),min(mape),max(mape))},'FontSize',10);
legend({'R²','MAPE (%)'},'Location','northeast','FontSize',9);
set(gca,'Box','off','XGrid','on','GridAlpha',0.3);

sgtitle({'5-Fold CV Stability — CatBoost Yield Regressor';
         'Low variance across folds confirms model robustness'}, ...
        'FontSize',12,'FontWeight','bold');

saveas(fig, 'yield_cv_scatter.png');
fprintf('Saved: yield_cv_scatter.png\n');
