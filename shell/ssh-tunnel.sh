echo -ne '\033]0;ssh-tunnel\007'
ssh -i ~/.ssh/aws-zang.pem -N -L 13306:aws-mysql.cnxghyednp7j.ap-northeast-1.rds.amazonaws.com:3306 ec2-user@54.238.212.115
echo -ne '\033]0;localhost\007'
