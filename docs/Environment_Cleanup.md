1. **Environment Cleanup**

   1. Review the setup and make     updates that reflect below (Ask questions when not clear):

      ​	a.    Base directory: /home/kmm/kevin/git/OpenBB

      ​	b.    Conda environment: OpenBB-env

      ​	c.    Move all .sh scripts to OpenBB/scripts

      ​	d.    Check all scripts can run from OpenBB/scripts and are updated to:

      ​	e.    Ensure all scripts use conda activate OpenBB-env

      ​	f.     http://localhost:8888/lab Jupyter Lab Base directory: /home/kmm/kevin/git/OpenBB/notebooks

      ​	g.    Default directory for market data to be accessible by notebooks: /home/kmm/kevin/git/OpenBB/market_data

   2. Run scripts/start_all.sh that all services successfully start

   3. Check that notebooks/SP500_momentum.ipynb can import openbb

   4. Commit changes in git if all steps are successful