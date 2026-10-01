const E=require('./engine');const rng=E.makeRng(+process.argv[3]||3);const N=+process.argv[2]||2000000;
const spins=+process.argv[4]||8;let s=0;for(let i=0;i<N;i++)s+=E.playFeature(rng,spins,E.MAX_WIN);
console.log(`Feature from ${spins} spins: avg ${(s/N).toFixed(2)}x bet over ${N}`);
