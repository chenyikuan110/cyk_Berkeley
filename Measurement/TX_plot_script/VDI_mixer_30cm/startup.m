
%{
set(groot, 'DefaultAxesColor', [25, 25, 25]/255);
set(groot, 'DefaultFigureColor', [25, 25, 25]/255);
set(groot, 'DefaultFigureInvertHardcopy', 'off');
colors = [241, 90, 90;
          240, 196, 25;
          78, 186, 111;
          45, 149, 191;
          149, 91, 165]/255;
set(groot, 'DefaultAxesColorOrder', colors);
set(groot, 'DefaultLineLineWidth', 3);

set(groot, 'DefaultTextColor', [1, 1, 1]);
set(groot, 'DefaultAxesXColor', [1, 1, 1]);
set(groot, 'DefaultAxesYColor', [1, 1, 1]);

set(groot, 'DefaultTextInterpreter', 'LaTeX');
set(groot, 'DefaultAxesTickLabelInterpreter', 'LaTeX');
set(groot, 'DefaultAxesFontName', 'LaTeX');
set(groot, 'DefaultLegendInterpreter', 'LaTeX');
%}


set(groot, 'DefaultLineLineWidth', 2.5, ...
           'DefaultTextInterpreter', 'LaTeX', ...
           'DefaultAxesTickLabelInterpreter', 'LaTeX', ...
           'DefaultAxesFontName', 'LaTeX', ...
           'DefaultLegendInterpreter', 'LaTeX', ...
           'DefaultAxesLineWidth', 1.5, ...
           'DefaultAxesFontSize', 24, ...
           'DefaultAxesBox', 'on', ...
           'DefaultAxesColor', [1, 1, 1], ...
           'DefaultFigureColor', [1, 1, 1], ...
           'DefaultFigureInvertHardcopy', 'off', ...
           'DefaultFigurePaperUnits', 'inches', ...
           'DefaultFigureUnits', 'inches', ...
           'DefaultFigurePosition', [0.1, 0.1, 8, 6]);
       
% colors = [241, 90, 90;
%   240, 196, 25;
%   78, 186, 111;
%   45, 149, 191;
%   149, 91, 165]/255;

colors = [
    0 0 0;
    0 0 255;
    255 0 255;
    0 255 255;
    0 255 0;
    255 0 0;
    255 255 0;
    129 52 190]/255;
set(groot, 'DefaultAxesColorOrder', colors);
set(groot, 'defaultFigureRenderer', 'painters')

format shorteng

%}

%set(groot, 'Default', struct())        %back to factory settings

