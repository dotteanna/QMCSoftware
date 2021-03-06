% make sure pwd = .../lds_sequences/
clc
clear
addpath(pwd)

dim = 1;
lattice_shift = rand(1,dim);
n_2powers = (1:20)';
lattice_times = n_2powers;
sobol_times = n_2powers;
halton_times = n_2powers;
trials = 40;
for i=1:size(n_2powers,1)
    % Lattice
    tic;
    for j=1:trials
      x_lat = gail.lattice_gen(1,2^i,dim);
      x_lat_shifted = mod(x_lat+lattice_shift,1);
    end
    lattice_times(i) = toc/trials;
    % Sobol
    tic;
    for j=1:trials
      sob = scramble(sobolset(dim),'MatousekAffineOwen');
      x_Sobol_scrambled = net(sob,2^i);
    end
    sobol_times(i) = toc/trials;
    % Halton 
    tic; 
    for j=1:trials
      h = scramble(haltonset(dim),'RR2');
      x_halton_scrambled = net(h,2^i);
    end
    halton_times(i) = toc/trials;
end

results = [2.^n_2powers, lattice_times, sobol_times, halton_times]
csvwrite('out/matlab_sequences.csv',results)
