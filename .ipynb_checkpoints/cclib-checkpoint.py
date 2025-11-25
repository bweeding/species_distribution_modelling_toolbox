import os
import numpy
import netCDF4
import datetime
import numpy
import matplotlib.pyplot as plt
import warnings
from scipy.stats import gamma, norm
from scipy.optimize import curve_fit, OptimizeWarning
from sklearn.metrics import r2_score

# Suppress only the specific OptimizeWarning
warnings.filterwarnings("ignore", category=OptimizeWarning)

def genplotpiani(fplot, xx, yy, seqx, seqy, xcdf, ycdf,
        seqp, xxis, yyis, yypred, dkor,
        pcor, gpar, rsq, hopt, drefname, dcorname):
    #pars = ' '.join([str(round(e, 2)) for e in gpar])
    pars = ''
    pa, pb, pc = [str(round(e, 5)) for e in hopt]
    eq = '$%sx^3 + %sx^2 + %sx$' % (pa, pb, pc)
    fig, axs = plt.subplot_mosaic('ABC;DDE;FFF', figsize=(15, 15))
    plt.subplots_adjust(hspace=0.35, wspace=0.35)
    # scatter
    axs['A'].scatter(xx, yy, color='black', label='corr:'+str(round(pcor,2)))
    axs['A'].legend()
    axs['A'].set_xlabel(dcorname)
    axs['A'].set_ylabel(drefname)
    # histogram
    axs['B'].hist(xx, bins=20, range=(min(seqx), max(seqx)), color='tab:blue')
    axs['C'].hist(yy, bins=20, range=(min(seqy), max(seqy)), color='tab:orange')
    axs['B'].title.set_text('Histogram ' + dcorname)
    axs['C'].title.set_text('Histogram ' + drefname)
    # cdf
    seqc = seqx[:] if max(seqx) > max(seqy) else seqy[:]
    axs['D'].plot(seqc, xcdf, color='tab:blue', label=dcorname)
    axs['D'].plot(seqc, ycdf, color='tab:orange', label=drefname)
    axs['D'].title.set_text('CDF')
    axs['D'].legend()
    axs['D'].grid()
    # fit fungsi poly
    axs['E'].scatter(xxis, yyis, color='dimgray', label='inv cdf')
    axs['E'].plot(xxis, yypred, color='tomato', label=eq)
    axs['E'].legend()
    # koreksi
    axs['F'].plot(xx, color='tab:blue', label=dcorname)
    axs['F'].plot(dkor, color='tab:purple', label=dcorname + ' (out)')
    axs['F'].legend()
    axs['F'].title.set_text('Correction')
    plt.savefig(fplot)
    plt.close()

# polynomial model to fit
def fpoly(x, a, b, c):
    return a * x**3 + b * x**2 + c * x

def findgamma(xx, yy):
    lmaxx = (max(xx) // 100) * 100 + 100
    lmaxy = (max(yy) // 100) * 100 + 100
    seqx = numpy.linspace(0, lmaxx, 100, endpoint=False)
    seqy = numpy.linspace(0, lmaxy, 100, endpoint=False)
    try:
        shapex, locx, scalex = gamma.fit(xx, floc=0)
        shapey, locy, scaley = gamma.fit(yy, floc=0)
    except:
        return False
    xcdf = gamma.cdf(seqx, a=shapex, loc=locx, scale=scalex)
    ycdf = gamma.cdf(seqy, a=shapey, loc=locy, scale=scaley)
    seqp = numpy.linspace(0, 1, 100, endpoint=False)
    xinv = gamma.ppf(seqp, a=shapex, loc=locx, scale=scalex)
    yinv = gamma.ppf(seqp, a=shapey, loc=locy, scale=scaley)
    return (xcdf, ycdf, xinv, yinv, seqx, seqy, seqp, shapex, locx, scalex, shapey, locy, scaley)


def findnormal(xx, yy):
    lminx = (min(xx) // 2) * 2 - 2
    lminy = (min(yy) // 2) * 2 - 2
    lmaxx = (max(xx) // 2) * 2 + 2
    lmaxy = (max(yy) // 2) * 2 + 2
    seqx = numpy.linspace(lminx, lmaxx, 100, endpoint=False)
    seqy = numpy.linspace(lminy, lmaxy, 100, endpoint=False)
    try:
        meanx, sdx = norm.fit(xx)
        meany, sdy = norm.fit(yy)
    except:
        return False
    xcdf = norm.cdf(seqx, meanx, sdx)
    ycdf = norm.cdf(seqy, meany, sdy)
    seqp = numpy.linspace(0, 1, 100, endpoint=False)
    xinv = norm.ppf(seqp, meanx, sdx)
    yinv = norm.ppf(seqp, meany, sdy)
    return (xcdf, ycdf, xinv, yinv, seqx, seqy, seqp, meanx, sdx, meany, sdy)

def calcpiani(xx, yy, pcor, fplot, drefname, dcorname, dmode):
    hasil = {}
    if dmode == 'gamma':
        pd = findgamma(xx, yy)
        if pd is False:
            return False
        xcdf, ycdf, xinv, yinv, seqx, seqy, seqp, shapex, locx, scalex, shapey, locy, scaley = pd
    elif dmode == 'normal':
        pd = findnormal(xx, yy)
        if pd is False:
            return False
        xcdf, ycdf, xinv, yinv, seqx, seqy, seqp, meanx, sdx, meany, sdy = pd
    else:
        return False
    xxis, yyis = [], []
    for x, y in zip(xinv, yinv):
        if x > 0 and y > 0:
            xxis.append(x)
            yyis.append(y)
    try:
        hopt, hcov = curve_fit(fpoly, xxis, yyis)
    except:
        return False
    # additional info
    yypred = [fpoly(x, *hopt) for x in xxis]
    rsq = r2_score(yyis, yypred)
    dkor = [fpoly(x, *hopt) for x in xx]
    #gpar = [shapex, locx, scalex, shapey, locy, scaley]
    gpar = []
    if fplot:
        genplotpiani(fplot, xx, yy, seqx, seqy, xcdf, ycdf,
            seqp, xxis, yyis, yypred, dkor,
            pcor, gpar, rsq, hopt, drefname, dcorname)
    return hopt.tolist()

def Savenc(namafile, lons, lats, vals, nama, satuan, misval):
    lenlons, lenlats = len(lons), len(lats)
    f = netCDF4.Dataset(namafile, 'w')
    f.createDimension("latitude", lenlats)
    f.createDimension("longitude", lenlons)
    varlat = f.createVariable("latitude", "f8", ("latitude",))
    varlat.units = 'degrees_north'
    varlat.axis = 'Y'
    varlat.standard_name = 'latitude'
    varlon = f.createVariable("longitude", "f8", ("longitude",))
    varlon.units = 'degrees_east'
    varlon.axis = 'X'
    varlon.standard_name = 'longitude'
    varval = f.createVariable(nama, "f8", ("latitude", "longitude"), zlib=True)
    varval.units = satuan
    varval.missing_value = misval
    varlat[:] = lats
    varlon[:] = lons
    varval[:] = vals
    f.close()

def Savenc3(namafile, lons, lats, vals, nama, satuan, misval, th0, bl0, tg0, tdelta, jtime):
    lenlons, lenlats = len(lons), len(lats)
    #since = 'days since ' + str(th0) + '-' + str(bl0).zfill(2) + '-' + str(tg0).zfill(2) + ' 00:00:00'
    since = 'days since 1900-01-01 00:00:00'
    if tdelta == 'days':
        tanggal = [datetime.datetime(th0, bl0, tg0) + x * datetime.timedelta(days=1) for x in range(jtime)]
    elif tdelta == 'months':
        tanggal = [datetime.datetime(th0 + ((bl0-1+x)//12), ((bl0-1+x) % 12) + 1, tg0) for x in range(jtime)]
    f = netCDF4.Dataset(namafile, 'w')
    f.createDimension("time", 0)
    f.createDimension("latitude", lenlats)
    f.createDimension("longitude", lenlons)
    vartime = f.createVariable("time", "f4", ("time",))
    vartime.units = since
    vartime.calendar = 'standard'
    varlat = f.createVariable("latitude", "f4", ("latitude",))
    varlat.units = 'degrees_north'
    varlat.axis = 'Y'
    varlat.standard_name = 'latitude'
    varlon = f.createVariable("longitude", "f4", ("longitude",))
    varlon.units = 'degrees_east'
    varlon.axis = 'X'
    varlon.standard_name = 'longitude'
    varval = f.createVariable(nama, "f8", ("time", "latitude", "longitude"), zlib=True)
    varval.units = satuan
    varval.missing_value = misval
    vartime[:] = netCDF4.date2num(tanggal, vartime.units, vartime.calendar)
    varlat[:] = lats
    varlon[:] = lons
    varval[:] = vals
    f.close()

