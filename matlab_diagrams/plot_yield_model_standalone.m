% =========================================================
% Chart 2 of 2: Yield Regressor — Standalone Performance
% One model, one task: predicting yield in kg/ha.
% No comparison — showing 5-fold CV results as a summary.
% =========================================================

rmse_cv = [2222.554, 2161.428, 2146.144, 2130.197, 2114.553];
mae_cv  = [1449.614, 1433.519, 1431.977, 1416.889, 1426.554];
r2_cv   = [0.7242,   0.7180,   0.7262,   0.7182,   0.7303];
mape_cv = [36.68,    37.68,    36.17,    36.91,    38.21];

mean_rmse = mean(rmse_cv);
mean_mae  = mean(mae_cv);
mean_r2   = mean(r2_cv);
mean_mape = mean(mape_cv);

fig = figure('Name','Yield Regressor — Standalone','Position',[100 100 820 420]);

blue   = [0.20 0.47 0.75];
orange = [0.85 0.33 0.10];
green  = [0.47 0.67 0.19];
red    = [0.64 0.08 0.18];

metrics  = {rmse_cv,    mae_cv,    r2_cv,     mape_cv};
labels   = {'RMSE (kg/ha)', 'MAE (kg/ha)', 'R²', 'MAPE (%)'};
means    = {mean_rmse,  mean_mae,  mean_r2,   mean_mape};
ylims    = {[2050 2350],[1380 1480],[0.710 0.740],[35 40]};
clrs     = {blue,       orange,    green,     red};
fmts     = {'%.0f',    '%.0f',    '%.4f',    '%.1f%%'};

for k = 1:4
    subplot(1,4,k);
    vals = metrics{k};
    b = bar(1:5, vals, 0.6, 'FaceColor', clrs{k}, 'EdgeColor','none','FaceAlpha',0.85);
    hold on;
    yline(means{k}, '--k', 'LineWidth', 1.4);
    text(4.6, means{k} + (ylims{k}(2)-ylims{k}(1))*0.015, ...
        ['Mean: ' sprintf(fmts{k}, means{k})], 'FontSize', 8, 'Color','k');
    for i = 1:5
        text(i, vals(i) + (ylims{k}(2)-ylims{k}(1))*0.012, ...
            sprintf(fmts{k}, vals(i)), 'HorizontalAlignment','center','FontSize',7.5);
    end
    xticks(1:5); xticklabels({'F1','F2','F3','F4','F5'});
    xlabel('CV Fold'); ylabel(labels{k});
    title(labels{k},'FontWeight','bold');
    ylim(ylims{k});
    set(gca,'Box','off','YGrid','on','GridAlpha',0.3);
    hold off;
end

sgtitle({'CatBoost Yield Regressor — 5-Fold Cross-Validation Performance';
         sprintf('Avg RMSE: %.0f kg/ha  |  Avg MAE: %.0f kg/ha  |  Avg R²: %.4f  |  Avg MAPE: %.1f%%', ...
                 mean_rmse, mean_mae, mean_r2, mean_mape)}, ...
        'FontSize',11,'FontWeight','bold');

saveas(fig, 'yield_model_standalone.png');
fprintf('Saved: yield_model_standalone.png\n');
