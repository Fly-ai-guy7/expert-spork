const E=require('./engine');const rng=E.makeRng(+process.argv[3]||3);const N=+process.argv[2]||2000000;
const mode=process.argv[5]||'classic';const spins=+process.argv[4]||E.featureSpins(3,mode);let s=0;for(let i=0;i<N;i++)s+=E.playFeature(rng,spins,E.MAX_WIN,mode);
console.log(`[${mode}] Feature from ${spins} spins: avg ${(s/N).toFixed(2)}x bet over ${N}`);
