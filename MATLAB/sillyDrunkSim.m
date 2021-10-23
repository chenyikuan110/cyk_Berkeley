clear
num = rand(10000,1);


% simulate all siturations where the drunk is not caught in the first two
% bars
% first bar & second bar
hit_count = 0;
miss_count = 0;
% not in first two bars
for i = 1:length(num)
    if( num(i)>0.6 )
        if(num(i)>0.9)
            miss_count = miss_count +1;
        else
            hit_count = hit_count+1;
        end
    end
end
% not in bar 1 and bar 3
for i = 1:length(num)
    if( ~(num(i)<0.3) && ~(num(i)>0.6 && num(i)<0.9))
        if(num(i)>0.9)
            miss_count = miss_count +1;
        else
            hit_count = hit_count+1;
        end
    end
end
% not in bar 2 and bar 3
for i = 1:length(num)
    if( ~(num(i)>0.6 && num(i)<0.9) && ~(num(i)>0.3 && num(i)<0.6))
        if(num(i)>0.9)
            miss_count = miss_count +1;
        else
            hit_count = hit_count+1;
        end
    end
end

hit_count/(hit_count+miss_count)

%%
clc
caught_in_third_bar = 0;
miss = 0;
caught = 0;
for i = 1:100000
    k = floor(rand()*3)+1; % the bar that the police didn't go to is random: 1,2,3
    j = rand(); % the location of the drunk man
    if(k == 1 && (j<0.3 || j>0.9)) % didn't go to the first bar initially
        if(j<0.3)
          caught_in_third_bar = caught_in_third_bar + 1;
        elseif(j>0.9)
          miss = miss+1;
        else
          caught = caught + 1;
        end
    end
    
    if(k == 2 && ((j<0.6 &&j>0.3) || j>0.9)) % didn't go to the second bar initially
        if(j<0.6 && j>0.3)
          caught_in_third_bar = caught_in_third_bar + 1;
        elseif(j>0.9)
          miss = miss+1;
        else
          caught = caught + 1;
        end
    end
    
    if(k == 3 && ((j<0.9 && j>0.6) || j>0.9)) % didn't go to the second bar initially
        if(j<0.9 && j>0.6)
          caught_in_third_bar = caught_in_third_bar + 1;
        elseif(j>0.9)
          miss = miss+1;
        else
          caught = caught + 1;
        end
    end   
end
caught_rate = caught/100000
caught_in_third_bar_rate = caught_in_third_bar/(caught_in_third_bar+miss)
in_the_third_bar_rate = caught_in_third_bar/100000