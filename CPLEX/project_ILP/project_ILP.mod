/*********************************************
 * OPL 12.6.0.0 Model
 * Author: AbYosh
 * Creation Date: 4 Nov 2014 at 15:10:13
 *********************************************/

 int num_data_structures	= ...;	//	number of data structures
 int num_memory_banks 		= ...;	//	number of memory banks (m+1 = external memory)
 int num_conflicts			= ...;	//	number of conflicts
 int p						= ...;	//	penalty
 int ext					= num_memory_banks+1;
 
 range n 		= 1..num_data_structures;
 range m 		= 1..num_memory_banks;
 range o 		= 1..num_conflicts;
 range m_ext 	= 1..num_memory_banks+1;
 range a 		= 1..num_data_structures;
 range b 		= 1..num_data_structures;
 
 float d 			= ...;	//	conflict cost 
 float s [i in n] 	= ...;	//	size of data structure i
 float c [j in m] 	= ...;	//	capacity of memory bank j
 float e [i in n] 	= ...;	//	access cost of data structure i
 
 dvar boolean x [i in n][j in m_ext];	//	binary matrix indication data structure in memory bank j
 dvar int y [k in o];					//	statuses
 
 minimize 
// 	sum(k in o)(y[k]*d) + sum(i in n)sum(j in m)e[i]*x[i][j] + p*sum(i in n)e[i]*x[i][ext];
 	sum(i in n)sum(j in m)e[i]*x[i][j] + p*sum(i in n)e[i]*x[i][ext];
 		//	Le he quitado "sum(k in o)(y[k]*d)" ya que lo veo sentido ponerlo
 		//	El costo de acceso se calcula mas con el resto de las sumatorias
 		
 subject to {
 	
 	y[1] == 0;
 	y[2] == 1;
 	y[3] == p;
 	y[4] == 2*p;
 	
 	forall(i in n)					//	(3)
 	  sum(j in m_ext) x[i][j] == 1;
 	  
 	forall(j in m)					//	(4)
 	  sum(i in n) x[i][j]*s[i] <= c[j];
 	   
 	forall(j in m)					//	(5)
 	  forall(c_a in a)
 	    forall(c_b in b)
 	      x[c_a][j] + x[c_b][j] <= 1+y[2];
 		    
 	forall(j in m)					//	(6)
 	  forall(c_a in a)
 	    forall(c_b in b)
 	      x[c_a][j] + x[c_b][ext] <= 1+(1/p)*y[3];
 		    
	forall(j in m)					//	(7)
	  forall(c_a in a)
	    forall(c_b in b)
	      x[c_a][ext] + x[c_b][j] <= 1+(1/p)*y[3];
 
 	forall(c_a in a)				//	(8)
 	  forall(c_b in b)
 	    x[c_a][ext] + x[c_b][ext] <= 1+(1/(2*p))*y[4];
 		
 }
 
 //	POST-PROCESSING BLOCK
execute {
 
 for (var j=1; j<=num_memory_banks; j++) {
	var load=0;
 	for (var i=1; i<=num_data_structures; i++) {
	  	load = load + (s[i]*x[i][j]);
 }  	
  	load = load * (1/c[j]) * 100;
  	writeln("Load in Memory Bank " + j + " at " + load + " %");
   
 }   
 writeln("x = DataStructures \\ MemoryBanks");
 for (var i=1; i<=num_data_structures; i++) {
 write("[");
 	for (var j=1; j<=num_memory_banks; j++) { 
	  write(" "+x[i][j]+" ");
	}
	write("] Size of DataStructure = "+s[i]+"\n");
	
}  
}; 