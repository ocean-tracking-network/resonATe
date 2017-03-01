

convert_file <- function(input_file){
  # Run the conversion script
  out = system2("/opt/anaconda/bin/python", 
                stdout = TRUE, stderr = TRUE, 
                args=list("/home/vagrant/otn-toolbox/common_r/cpr.py","conversion","conversion",
                          paste("'",input_file,"'",sep='')))
  for (line in out){
    print(line)
  }
}