module calibration(in1,outp1);

input in1;
output outp1;
wire out0;

INV_X4 inv0(.ZN(out0),.A(in1));
INV_X4 inv1(.ZN(outp1),.A(out0));

endmodule
