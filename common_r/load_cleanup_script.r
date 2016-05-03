cleanup <- function(){
  
  out = system2("/opt/anaconda/bin/python",  
                stdout = TRUE, stderr = TRUE, 
                args=list("/home/vagrant/otn-toolbox/common_r/cpr.py", "cleanup","cleanup","reqcleanup"))
  for (line in out){
    print(line)
  }
}